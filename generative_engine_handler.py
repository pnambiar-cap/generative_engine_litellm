import requests
import json
import time
import yaml
from typing import Iterator, AsyncIterator, Any, Optional, Union
from litellm import CustomLLM
from litellm.types.utils import GenericStreamingChunk, ModelResponse, ImageResponse
import litellm

class GenerativeEngineLLM(CustomLLM):
    def __init__(self, api_base: str = "https://api.generative.engine.capgemini.com/v1"):
        super().__init__()
        self.api_base = api_base
        self.config = self.load_config()
        self.api_key = self.config["litellm_settings"]["generative_engine_api_key"]
        self.provider = self.config["litellm_settings"].get("generative_engine_provider", "capgemini")
        self.interface = self.config["litellm_settings"].get("generative_engine_interface", "default")
        self.mode = self.config["litellm_settings"].get("generative_engine_mode", "default")
        self.headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def load_config(self):
        with open("config.yaml", "r") as config_file:
            return yaml.safe_load(config_file)

    def completion(self, model: str, messages: list, *args, **kwargs) -> ModelResponse:
        url = f"{self.api_base}/llm/invoke"
        
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

        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()

            content = ""
            for line in response.text.split('\n'):
                if line.startswith('data: '):
                    try:
                        json_data = json.loads(line[6:])
                        if json_data['action'] == 'final_response':
                            content = json_data['data']['content']
                            break
                    except json.JSONDecodeError:
                        continue

            return ModelResponse(
                id=f"geneng-{time.time()}",
                choices=[{
                    "message": {"role": "assistant", "content": content.strip()},
                    "finish_reason": "stop"
                }],
                model=model,
                usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}  # Placeholder values
            )

        except requests.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")

    def streaming(self, model: str, messages: list, *args, **kwargs) -> Iterator[GenericStreamingChunk]:
        url = f"{self.api_base}/llm/invoke"
        
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

        try:
            with requests.post(url, headers=self.headers, json=payload, stream=True) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if line.startswith(b'data: '):
                        try:
                            json_data = json.loads(line[6:])
                            if json_data['action'] == 'token':
                                yield GenericStreamingChunk(
                                    text=json_data['data']['token'],
                                    is_finished=False
                                )
                            elif json_data['action'] == 'final_response':
                                yield GenericStreamingChunk(
                                    text=json_data['data']['content'],
                                    is_finished=True,
                                    finish_reason="stop"
                                )
                                break
                        except json.JSONDecodeError:
                            continue
        except requests.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")

    # Implement async methods if needed
    async def acompletion(self, *args, **kwargs) -> ModelResponse:
        # Implement async completion
        pass

    async def astreaming(self, *args, **kwargs) -> AsyncIterator[GenericStreamingChunk]:
        # Implement async streaming
        pass

# Usage
generative_engine_llm = GenerativeEngineLLM()

# Register the custom handler
litellm.custom_provider_map = [
    {"provider": "generative-engine", "custom_handler": generative_engine_llm}
]