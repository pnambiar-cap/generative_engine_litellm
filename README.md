# Capgemini Generative Engine LiteLLM Integration

This repository provides the necessary files to integrate the Capgemini Generative Engine API with LiteLLM, allowing for seamless use of the Generative Engine within the LiteLLM ecosystem.

## Overview

- **Custom Handler**: A custom LiteLLM handler (`generative_engine_handler.py`) that interfaces with the Capgemini Generative Engine API.
- **Configuration**: A flexible configuration system using `generative_engine_config.yaml` and environment variables.
- **Test Script**: A test script (`test_generative_engine_litellm.py`) to demonstrate usage of the custom handler with multiple models.

## Repository Contents

- `generative_engine_litellm/`: The Python package directory containing the custom handler.
    - `generative_engine_handler.py`: The custom LiteLLM handler.
- `tests/`: Directory containing test scripts.
    - `test_generative_engine_litellm.py`: Test script demonstrating usage.
- `setup.py`: Setup script for installing the package.
- `generative_engine_config.yaml`: Sample configuration file (should be created by the user).
- `README.md`: This documentation file.

## Installation

### Prerequisites

- Python 3.7 or higher
- pip package manager

### Steps

1. **Clone the Repository**

    ```bash
    git clone https://github.com/pnambiar-cap/generative_engine_litellm.git
    cd generative_engine_litellm
    ```

2. **Install Dependencies**

    Install the required packages, preferably in a virtual environment:

    ```bash
    pip install -r requirements.txt
    ```

    If `requirements.txt` is not provided, install the packages manually:

    ```bash
    pip install litellm pyyaml requests
    ```

3. **Install the Package in Editable Mode**

    Install the package locally to resolve imports:

    ```bash
    pip install -e .
    ```

## Configuration

### Create `generative_engine_config.yaml`

Create a configuration file named `generative_engine_config.yaml` in the root directory of the repository. This file contains both general and model-specific configurations.

**Example `generative_engine_config.yaml`:**

```yaml
generative_engine:
  GENERATIVE_ENGINE_API_KEY: 'your-api-key-here'
  GENERATIVE_ENGINE_API_BASE: 'https://api.generative.engine.capgemini.com'
  GENERATIVE_ENGINE_API_ENDPOINT: '/v2/llm/invoke'

anthropic.claude-v2:
  GENERATIVE_ENGINE_MODEL_INTERFACE: 'langchain'
  GENERATIVE_ENGINE_MODEL_MODE: 'chain'
  GENERATIVE_ENGINE_MODEL_PROVIDER: 'bedrock'

openai.gpt-3.5-turbo:
  GENERATIVE_ENGINE_MODEL_INTERFACE: 'default'
  GENERATIVE_ENGINE_MODEL_MODE: 'default'
  GENERATIVE_ENGINE_MODEL_PROVIDER: 'openai'

google.palm-2:
  GENERATIVE_ENGINE_MODEL_INTERFACE: 'custom'
  GENERATIVE_ENGINE_MODEL_MODE: 'advanced'
  GENERATIVE_ENGINE_MODEL_PROVIDER: 'google'
```

- Replace `'your-api-key-here'` with your actual Capgemini Generative Engine API key.
- Add or modify model-specific configurations as needed.

### Secure Your Configuration File

Add `generative_engine_config.yaml` to your `.gitignore` file to prevent accidental commits of sensitive information:

```plaintext
# .gitignore
generative_engine_config.yaml
```

## Usage

### Running the Test Script

The test script demonstrates how to use the custom handler with multiple models.

```bash
python tests/test_generative_engine_litellm.py
```

**Expected Output**: The script will test each model specified in the `models_to_test` list and output the assistant's responses.

### Using the Custom Handler in Your Code

Below is an example of how to integrate the custom handler into your own application.

```python
import os
import logging
import litellm

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Specify the path to your configuration file
config_path = os.path.join(os.getcwd(), 'generative_engine_config.yaml')

# Import the custom handler
from generative_engine_litellm.generative_engine_handler import GenerativeEngineLLM

# Initialize the custom handler with the config path
generative_engine_llm = GenerativeEngineLLM(config_path=config_path)

# Register the custom handler with LiteLLM
litellm.custom_provider_map = [
    {"provider": "generative-engine", "custom_handler": generative_engine_llm}
]

logger.info(f"Custom provider map: {litellm.custom_provider_map}")

# Example function to test completion with a specific model
def test_completion_with_model(model_name):
    try:
        # Include the provider prefix in the model name
        full_model_name = f'generative-engine/{model_name}'
        response = litellm.completion(
            model=full_model_name,
            messages=[{"role": "user", "content": "What is the capital of France?"}]
        )
        logger.info(f"Completion Response for model {full_model_name}:")
        if response and response.choices and response.choices[0].message:
            logger.info(f"Content: {response.choices[0].message.content}")
        else:
            logger.info("No content in the response")
    except Exception as e:
        logger.error(f"Completion Error for model {model_name}: {str(e)}")

# Example usage
if __name__ == "__main__":
    models_to_test = [
        'anthropic.claude-v2',
        'openai.gpt-3.5-turbo',
        'google.palm-2',
    ]

    for model_name in models_to_test:
        logger.info(f"Testing model: {model_name}")
        test_completion_with_model(model_name)
        logger.info("\n" + "="*50 + "\n")
```

**Notes**:

- Ensure that the model names match those in your `generative_engine_config.yaml` file.
- The provider prefix `'generative-engine/'` is required in the model parameter for LiteLLM to route the request to the custom handler.

## Customization

### Adding New Models

To add a new model, update your `generative_engine_config.yaml` with the model-specific configurations:

```yaml
new.model.name:
  GENERATIVE_ENGINE_MODEL_INTERFACE: 'your_interface'
  GENERATIVE_ENGINE_MODEL_MODE: 'your_mode'
  GENERATIVE_ENGINE_MODEL_PROVIDER: 'your_provider'
```

- Replace `'new.model.name'` with the actual model name.
- Update the configurations as needed.

### Adjusting Configurations

You can adjust the general and model-specific configurations to suit your needs. Remember to keep sensitive information secure.

## Security Note

Keep your `generative_engine_config.yaml` file secure and do not commit it to any public repositories. Ensure it's included in your `.gitignore` file.

## Troubleshooting

### Common Issues

- **Configuration File Not Found**: Ensure that `generative_engine_config.yaml` is in the correct location and that the `config_path` is specified correctly.
- **API Key Missing**: Verify that your API key is correctly set in the configuration file.
- **Import Errors**: Make sure the package is installed in editable mode and that the imports in your scripts are correct.

### Logging

Adjust the logging level in your scripts to get more detailed output:

```python
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

Contributions to improve the integration are welcome. Please feel free to submit issues or pull requests.
