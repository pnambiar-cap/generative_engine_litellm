import litellm
from litellm import completion
import uuid
import yaml
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_config():
    with open("config.yaml", "r") as config_file:
        return yaml.safe_load(config_file)

config = load_config()
model_name = config['litellm_settings']['generative_engine_model']

# Load the custom handler
from generative_engine_handler import GenerativeEngineLLM

# Create an instance of the custom handler
generative_engine_llm = GenerativeEngineLLM()

# Register the custom handler
litellm.custom_provider_map = [
    {"provider": "generative-engine", "custom_handler": generative_engine_llm}
]

logger.info(f"Custom provider map: {litellm.custom_provider_map}")

def test_completion():
    try:
        response = completion(
            model=model_name,
            messages=[{"role": "user", "content": "What is the capital of France?"}]
        )
        logger.info("Completion Response:")
        logger.debug(f"Raw response: {response}")
        if response and response.choices and response.choices[0].message:
            logger.info(f"Content: {response.choices[0].message.content}")
        else:
            logger.info("No content in the response")
    except Exception as e:
        logger.error(f"Completion Error: {str(e)}")

def test_completion_with_session():
    session_id = str(uuid.uuid4())
    logger.info(f"Starting session with ID: {session_id}")
    
    try:
        # First message
        logger.info("Sending first message...")
        response1 = completion(
            model=model_name,
            messages=[{"role": "user", "content": "Hello, who are you?"}],
            session_id=session_id
        )
        logger.info("First Response:")
        logger.info(f"Raw response: {response1}")
        if response1 and hasattr(response1, 'choices') and response1.choices and response1.choices[0].message:
            logger.info(f"Content: {response1.choices[0].message.content}")
        else:
            logger.info("No content in the first response")

        # Second message
        logger.info("Sending second message...")
        response2 = completion(
            model=model_name,
            messages=[
                {"role": "user", "content": "Hello, who are you?"},
                {"role": "assistant", "content": response1.choices[0].message.content if response1.choices else ""},
                {"role": "user", "content": "What did I just ask you?"}
            ],
            session_id=session_id
        )
        logger.info("Second Response:")
        logger.info(f"Raw response: {response2}")
        if response2 and hasattr(response2, 'choices') and response2.choices and response2.choices[0].message:
            logger.info(f"Content: {response2.choices[0].message.content}")
        else:
            logger.info("No content in the second response")

    except Exception as e:
        logger.error(f"Session Completion Error: {str(e)}")
        logger.exception("Full traceback:")

if __name__ == "__main__":
    logger.info("Testing basic completion:")
    test_completion()
    logger.info("\n" + "="*50 + "\n")
    
    logger.info("Testing completion with session:")
    test_completion_with_session()