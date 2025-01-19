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
    pip install  .
    ```

## Configuration

### Create `generative_engine_config.yaml`

Create a configuration file named `generative_engine_config.yaml` in the root directory of the repository. This file contains both general and model-specific configurations.

**Example `generative_engine_config.yaml`:**

```yaml
generative_engine:
  GENERATIVE_ENGINE_API_KEY: 'your-api-key'
  GENERATIVE_ENGINE_API_BASE: 'https://api.generative.engine.capgemini.com'
  GENERATIVE_ENGINE_API_ENDPOINT: '/v2/llm/invoke'

anthropic.claude-v2:
  GENERATIVE_ENGINE_MODEL_INTERFACE: 'langchain'
  GENERATIVE_ENGINE_MODEL_MODE: 'chain'
  GENERATIVE_ENGINE_MODEL_PROVIDER: 'bedrock'

openai.gpt-3.5-turbo:
  GENERATIVE_ENGINE_MODEL_INTERFACE: 'langchain'
  GENERATIVE_ENGINE_MODEL_MODE: 'chain'
  GENERATIVE_ENGINE_MODEL_PROVIDER: 'azure'

openai.gpt-4o:
  GENERATIVE_ENGINE_MODEL_INTERFACE: 'langchain'
  GENERATIVE_ENGINE_MODEL_MODE: 'chain'
  GENERATIVE_ENGINE_MODEL_PROVIDER: 'azure'

openai.o1-mini:
  GENERATIVE_ENGINE_MODEL_INTERFACE: 'langchain'
  GENERATIVE_ENGINE_MODEL_MODE: 'chain'
  GENERATIVE_ENGINE_MODEL_PROVIDER: 'azure'

openai.o1-preview:
  GENERATIVE_ENGINE_MODEL_INTERFACE: 'langchain'
  GENERATIVE_ENGINE_MODEL_MODE: 'chain'
  GENERATIVE_ENGINE_MODEL_PROVIDER: 'azure'

us.meta.llama3-2-3b-instruct-v1:0:
  GENERATIVE_ENGINE_MODEL_INTERFACE: 'langchain'
  GENERATIVE_ENGINE_MODEL_MODE: 'chain'
  GENERATIVE_ENGINE_MODEL_PROVIDER: 'bedrock'
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

1. To run the test script:
   ```sh
   python test_generative_engine_litellm.py
   ```
   This will demonstrate both streaming and non-streaming completions using the Generative Engine.

2. To use in your own code:
   ```python
   import litellm
   from litellm import completion
   from generative_engine_handler import generative_engine_llm
   # Get the path to the configuration file
   config_path = os.path.join(os.getcwd(), 'generative_engine_config.yaml')
   # Load the custom handler with the config path
   from generative_engine_litellm.generative_engine_handler import GenerativeEngineLLM
   generative_engine_llm = GenerativeEngineLLM(config_path=config_path)

   # Register the custom handler
   litellm.custom_provider_map = [
       {"provider": "generative-engine", "custom_handler": generative_engine_llm}
   ]

   # Use the model
   response = completion(
       #example model-name - anthropic.claude-v2, ensure 
       model="generative-engine/model-name", 
       messages=[{"role": "user", "content": "Your prompt here"}]
   )
   print(response.choices[0].message.content)
   ```

## Customization

- You can modify the `model_list` in `config.yaml` to add more models or change the existing one.
- Adjust the API base URL in `generative_engine_handler.py` if needed.

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
