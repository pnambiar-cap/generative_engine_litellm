# test_generative_engine_litellm.py

import os
import logging
import uuid
import litellm

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the path to the configuration file
config_path = os.path.join(os.getcwd(), 'generative_engine_config.yaml')

# Load the custom handler with the config path
from generative_engine_litellm.generative_engine_handler import GenerativeEngineLLM
generative_engine_llm = GenerativeEngineLLM(config_path=config_path)

# Register the custom handler
litellm.custom_provider_map = [
    {"provider": "generative-engine", "custom_handler": generative_engine_llm}
]

logger.info(f"Custom provider map: {litellm.custom_provider_map}")

def test_completion_with_model(model_name):
    try:
        # Include the provider prefix in the model name
        full_model_name = f'generative-engine/{model_name}'
        response = litellm.completion(
            model=full_model_name,
            messages=[{"role": "user", "content": "What is the capital of France?"}]
        )
        logger.info(f"Completion Response for model {full_model_name}:")
        logger.debug(f"Raw response: {response}")
        if response and response.choices and response.choices[0].message:
            logger.info(f"Content: {response.choices[0].message.content}")
        else:
            logger.info("No content in the response")
    except Exception as e:
        logger.error(f"Completion Error for model {model_name}: {str(e)}")

if __name__ == "__main__":
    # List of models to test (without provider prefix)
    models_to_test = [
        'anthropic.claude-v2',
        'openai.gpt-3.5-turbo',
        'openai.gpt-4o',
        'openai.o1-preview',
        'openai.o1-mini',
        'us.meta.llama3-2-3b-instruct-v1:0',
    ]

    for model_name in models_to_test:
        logger.info(f"Testing model: {model_name}")
        test_completion_with_model(model_name)
        logger.info("\n" + "="*50 + "\n")
