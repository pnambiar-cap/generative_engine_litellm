# generative_engine_handler.py

import os
import requests
import json
import time
import logging
from typing import Iterator, List
from litellm import CustomLLM
from litellm.types.utils import GenericStreamingChunk, ModelResponse
import litellm
import yaml

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

class GenerativeEngineLLM(CustomLLM):
    def __init__(self, config_path=None):
        super().__init__()
        # Load configuration from generative_engine_config.yaml or environment variables
        self.config_path = config_path or os.getenv('GENERATIVE_ENGINE_CONFIG_PATH')
        self.config = self.load_config()

        # Load general configuration values
        general_config = self.config.get('generative_engine', {})
        self.api_base = self.get_config_value('GENERATIVE_ENGINE_API_BASE', general_config, default='https://api.generative.engine.capgemini.com')
        self.api_endpoint = self.get_config_value('GENERATIVE_ENGINE_API_ENDPOINT', general_config, default='/v2/llm/invoke')
        self.api_key = self.get_config_value('GENERATIVE_ENGINE_API_KEY', general_config, required=True)

        self.headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        logger.info(f"Initialized GenerativeEngineLLM with API base: {self.api_base}")

    def load_config(self):
        config = {}
        if self.config_path and os.path.exists(self.config_path):
            config_path = self.config_path
        else:
            # Fallback to default location in the same directory as this file
            config_path = os.path.join(os.path.dirname(__file__), 'generative_engine_config.yaml')

        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as config_file:
                    config = yaml.safe_load(config_file)
                    logger.info(f"Loaded configuration from {config_path}")
            except Exception as e:
                logger.error(f"Failed to load configuration file: {e}")
        else:
            logger.info("Configuration file generative_engine_config.yaml not found; will use environment variables")
        return config

    def get_config_value(self, key, config_section, default=None, required=False):
        # First, try to get the value from the provided config section
        value = config_section.get(key)
        if value is not None:
            return value
        # Next, try to get the value from environment variables
        value = os.getenv(key)
        if value is not None:
            return value
        # If the value is required and not found, raise an error
        if required:
            raise ValueError(f"{key} is required but not found in config section or environment variables")
        # Return the default value if provided
        return default

    def completion(self, model: str, messages: List[dict], *args, **kwargs) -> ModelResponse:
        url = f"{self.api_base}{self.api_endpoint}"

        # Print all the positional arguments received
        logger.debug(f"Positional arguments received: {args}")
        logger.debug(f"Keyword arguments received: {kwargs}")
        # Combine messages into a single prompt
        prompt = " ".join([m["content"] for m in messages])
        logger.info(f"model : {model} - Received prompt: {prompt}")

        # Get model-specific configurations
        model_config = self.config.get(model, {})
        if not model_config:
            logger.warning(f"No configuration found for model '{model}'; using defaults")

        # Load model-specific configuration values
        model_interface = self.get_config_value('GENERATIVE_ENGINE_MODEL_INTERFACE', model_config, default='langchain')
        model_mode = self.get_config_value('GENERATIVE_ENGINE_MODEL_MODE', model_config, default='chain')
        model_provider = self.get_config_value('GENERATIVE_ENGINE_MODEL_PROVIDER', model_config, default='bedrock')

        # Extract max_tokens from optional_params if available
        optional_params = kwargs.get('optional_params', {})
        max_token_value = optional_params.get('max_tokens', kwargs.get("max_tokens", 4096)) # Default Max Tokens value is 4096
        logger.info(f"Setting max_token_value {max_token_value} for model {model}")

        payload = {
            "action": "run",
            "modelInterface": model_interface,
            "data": {
                "text": prompt,
                "files": [],
                "modelName": model,
                "provider": model_provider,
                "mode": model_mode,
                "modelKwargs": {
                    "maxTokens": max_token_value,
                    "temperature": kwargs.get("temperature", 0.6),
                    "streaming": False,
                    "topP": kwargs.get("top_p", 0.9)
                }
            }
        }

    
        session_id = kwargs.get("session_id")
        if session_id:
            payload["data"]["sessionId"] = session_id
            logger.info(f"Using session ID: {session_id}")

        logger.info(f"Sending request to {url}")
        logger.debug(f"Headers: {json.dumps(self.headers)}")
        logger.debug(f"Payload: {json.dumps(payload)}")

        timeout_value = kwargs.get("timeout", 120)
        logger.info(f"Setting timeout to {timeout_value} seconds")

        start_time = time.time()

        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=timeout_value)
            response.raise_for_status()
            logger.debug(f"Received response: {response.text}")

            json_response = response.json()
            content = json_response.get("content", "")
            session_id = json_response.get("sessionId", "")
            usage = json_response.get("metadata", {}).get("usage", {})

            logger.debug(f"Extracted content: {content}")
            logger.debug(f"Session ID: {session_id}")
            # Check if the response contains an error message
            
            if "Exception" in content or "An error has occurred" in content:
                logger.error(f"Error found in response content: {content}")
                raise Exception(f"API response contains an error: {content}")
            
            model_response = ModelResponse(
                id=f"geneng-{time.time()}",
                choices=[{
                    "message": {"role": "assistant", "content": content.strip()},
                    "finish_reason": "stop"
                }],
                model=model,
                usage={
                    "prompt_tokens": usage.get("input_tokens", 0),
                    "completion_tokens": usage.get("output_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0)
                }
            )

            logger.debug(f"Created ModelResponse: {model_response}")
            
            if model_response and model_response.choices and model_response.choices[0].message:
                logger.info(f"model response content: {model_response.choices[0].message.content}")
            else:
                logger.info("No content in the response")

            end_time = time.time()
            elapsed_time = end_time - start_time
            logger.info(f"Request took {elapsed_time:.2f} seconds")

            return model_response

        except requests.RequestException as e:
            end_time = time.time()
            elapsed_time = end_time - start_time
            logger.info(f"Request failed after {elapsed_time:.2f} seconds")
            logger.info(f"API request failed: {str(e)}")
            if e.response:
                logger.error(f"Response status code: {e.response.status_code}")
                logger.error(f"Response headers: {e.response.headers}")
                logger.error(f"Response content: {e.response.content}")
            else:
                logger.error("No response received")
            raise Exception(f"API request failed: {str(e)}")

    # The streaming method can be updated similarly if needed

# Do not initialize or register the handler here if you plan to import this module elsewhere
