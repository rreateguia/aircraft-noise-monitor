
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Connect to OpenRouter
client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

# Send a message to the model
response = client.chat.completions.create(
    model=os.getenv("OPENROUTER_MODEL"),
    messages=[
        {
            "role": "user",
            "content": "Explain what an AI coding agent is in two sentences."
        }
    ]
)

# Display the response
print(response.choices[0].message.content)
