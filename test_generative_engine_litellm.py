import litellm
from litellm import completion

# Load the custom handler
from generative_engine_handler import generative_engine_llm

# Register the custom handler
litellm.custom_provider_map = [
    {"provider": "generative-engine", "custom_handler": generative_engine_llm}
]

def test_completion():
    try:
        response = completion(
            model="generative-engine-model",
            messages=[{"role": "user", "content": "What is the capital of France?"}]
        )
        print("Completion Response:")
        print(response.choices[0].message.content)
    except Exception as e:
        print(f"Completion Error: {str(e)}")

def test_streaming():
    try:
        response = completion(
            model="generative-engine-model",
            messages=[{"role": "user", "content": "Count from 1 to 5."}],
            stream=True
        )
        print("Streaming Response:")
        for chunk in response:
            print(chunk.choices[0].delta.content, end="", flush=True)
        print()  # New line after streaming is complete
    except Exception as e:
        print(f"Streaming Error: {str(e)}")

if __name__ == "__main__":
    test_completion()
    print("\n" + "="*50 + "\n")
    test_streaming()