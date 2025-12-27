import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def init_chat_completion(messages, model="gpt-4", temperature=0.7, max_tokens=None):
    """
    Initialize and execute a chat completion request.
    
    Args:
        messages (list): List of message dictionaries with 'role' and 'content'
        model (str): The model to use (default: gpt-4)
        temperature (float): Sampling temperature (default: 0.7)
        max_tokens (int): Maximum tokens in response (default: None)
    
    Returns:
        str: The assistant's response content
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error during chat completion: {e}")
        return None


# Example usage
if __name__ == "__main__":
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello! Can you explain what OpenAI is?"}
    ]
    
    response = init_chat_completion(messages)
    if response:
        print("Assistant:", response)
