# Capgemini Generative Engine LiteLLM Integration

This repository contains the necessary files to integrate the Capgemini Generative Engine API with LiteLLM, allowing for easy use of the Generative Engine within the LiteLLM ecosystem.

## Files

1. `generative_engine_handler.py`: Contains the custom LiteLLM handler for the Capgemini Generative Engine API.
2. `config.yaml`: Configuration file for LiteLLM, including model settings and API key.
3. `test_generative_engine.py`: A test script to demonstrate usage of the custom handler.

## Installation

1. Clone this repository:
   ```sh
   git clone https://github.com/pnambiar-cap/generative-engine-litellm.git
   cd generative-engine-litellm
   ```

2. Install the required dependencies:
   ```sh
   pip install litellm pyyaml requests
   ```

## Configuration

1. Copy `config.yaml.sample` to `config.yaml` and replace `your-api-key-here` with your actual Capgemini Generative Engine API key:
   ```yaml
   litellm_settings:
     generative_engine_api_key: "your-api-key-here"
   ```

## Usage

1. To run the test script:
   ```sh
   python test_generative_engine_litellm.py
   ```
   This will demonstrate both streaming and non-streaming completions using the Generative Engine.

2. To use in your own code:

```python
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

# Run the test function
test_completion()
```

## Customization

- You can modify the  `config.yaml` update the model you want to use
  

## Security Note

Remember to keep your `config.yaml` file secure and never commit it with your actual API key to a public repository. config.yaml is in .gitignore file.

## Contributing

Contributions to improve the integration are welcome. Please feel free to submit issues or pull requests.



