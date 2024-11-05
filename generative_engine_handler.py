import requests
import json
import time
import logging
import yaml
from enum import Enum
from typing import Any, AsyncIterator, Iterator, List, Optional, Union
from litellm import CustomLLM
from litellm.types.utils import GenericStreamingChunk, ModelResponse, ImageResponse
import litellm

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

class GenerativeEngineLLM(CustomLLM):
    def __init__(self):
        super().__init__()
        self.config = self.load_config()
        self.api_base = self.config["litellm_settings"]["generative_engine_api_base"]
        self.api_endpoint = self.config["litellm_settings"]["generative_engine_api_endpoint"]
        self.api_key = self.config["litellm_settings"]["generative_engine_api_key"]
        self.provider = self.config["litellm_settings"].get("generative_engine_provider", "capgemini")
        self.interface = self.config["litellm_settings"].get("generative_engine_interface", "default")
        self.mode = self.config["litellm_settings"].get("generative_engine_mode", "default")
        self.headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        logger.info(f"Loaded config: {self.config}")

    def load_config(self):
        with open("config.yaml", "r") as config_file:
            return yaml.safe_load(config_file)

    def completion(self, model: str, messages: list, *args, **kwargs) -> ModelResponse:
        url = f"{self.api_base}{self.api_endpoint}"
        
        prompt = " ".join([m["content"] for m in messages])
        
        payload = {
            "action": "run",
            "modelInterface": self.interface,
            "data": {
                "text": prompt,
                "files": [],
                "modelName": model,
                "provider": self.provider,
                "modelKwargs": {
                    "maxTokens": kwargs.get("max_tokens", 512),
                    "temperature": kwargs.get("temperature", 0.6),
                    "streaming": False,
                    "topP": kwargs.get("top_p", 0.9)
                }
            }
        }

        if self.mode != "default":
            payload["data"]["mode"] = self.mode

        session_id = kwargs.get("session_id")
        if session_id:
            payload["data"]["sessionId"] = session_id
            logger.info(f"Using session ID: {session_id}")

        logger.info(f"Sending request to {url}")
        logger.info(f"Headers: {json.dumps(self.headers)}")
        logger.info(f"Payload: {json.dumps(payload)}")

        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=60)
            response.raise_for_status()
            logger.info(f"Received response: {response.text}")

            json_response = response.json()
            content = json_response.get("content", "")
            session_id = json_response.get("sessionId", "")
            usage = json_response.get("metadata", {}).get("usage", {})

            logger.info(f"Extracted content: {content}")
            logger.info(f"Session ID: {session_id}")

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

            logger.info(f"Created ModelResponse: {model_response}")

            return model_response

        except requests.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            logger.error(f"Response status code: {e.response.status_code if e.response else 'No response'}")
            logger.error(f"Response headers: {e.response.headers if e.response else 'No response'}")
            logger.error(f"Response content: {e.response.content if e.response else 'No response'}")
            raise Exception(f"API request failed: {str(e)}")

    def streaming(self, model: str, messages: List[dict], *args, **kwargs) -> Iterator[GenericStreamingChunk]:
        url = f"{self.api_base}{self.api_endpoint}"
        
        prompt = " ".join([m["content"] for m in messages])
        
        payload = {
            "action": "run",
            "modelInterface": self.interface,
            "data": {
                "text": prompt,
                "files": [],
                "modelName": model,
                "provider": self.provider,
                "modelKwargs": {
                    "maxTokens": kwargs.get("max_tokens", 512),
                    "temperature": kwargs.get("temperature", 0.6),
                    "streaming": True,
                    "topP": kwargs.get("top_p", 0.9)
                }
            }
        }

        if self.mode != "default":
            payload["data"]["mode"] = self.mode

        session_id = kwargs.get("session_id")
        if session_id:
            payload["data"]["sessionId"] = session_id
            logger.info(f"Using session ID: {session_id}")

        logger.info(f"Final payload: {json.dumps(payload)}")

        timeout = kwargs.get("timeout", 60)

        logger.info(f"Sending streaming request to {url}")
        logger.info(f"Payload: {json.dumps(payload)}")

        try:
            with requests.post(url, headers=self.headers, json=payload, stream=True, timeout=timeout) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if line:
                        line = line.decode('utf-8')
                        if line.startswith('data: '):
                            try:
                                json_data = json.loads(line[6:])
                                action_type = json_data.get('action')
                                if action_type == 'token':
                                    yield GenericStreamingChunk(
                                        text=json_data['data']['token'],
                                        is_finished=False
                                    )
                                elif action_type == 'final_response':
                                    yield GenericStreamingChunk(
                                        text=json_data['data']['content'],
                                        is_finished=True,
                                        finish_reason="stop"
                                    )
                                    break
                            except json.JSONDecodeError:
                                logger.warning(f"Failed to parse JSON: {line}")
        except requests.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            logger.error(f"Response status code: {e.response.status_code if e.response else 'No response'}")
            logger.error(f"Response headers: {e.response.headers if e.response else 'No response'}")
            logger.error(f"Response content: {e.response.content if e.response else 'No response'}")
            raise Exception(f"API request failed: {str(e)}")

generative_engine_llm = GenerativeEngineLLM()

# Register the custom handler
litellm.custom_provider_map =  [ 
    {"provider": "generative-engine", "custom_handler": generative_engine_llm}
    ]   


