
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)


# Actual Python function
def list_files():
    files = []

    for path in PROJECT_ROOT.iterdir():
        if path.is_file() and not path.name.startswith("."):
            files.append(path.name)

    return files


# Tool description given to the LLM
tools = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List the files in the project root directory.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]


# Ask the LLM
response = client.chat.completions.create(
    model=os.getenv("OPENROUTER_MODEL"),
    messages=[
        {
            "role": "user",
            "content": "Show me the files in this project."
        }
    ],
    tools=tools,
    tool_choice="auto"
)


# Inspect the response
message = response.choices[0].message
if message.tool_calls:
    messages = [
        {
            "role": "user",
            "content": "Show me the files in this project."
        }
    ]

    # Add the assistant's tool-call request to the conversation
    messages.append(message)

    for tool_call in message.tool_calls:
        if tool_call.function.name == "list_files":
            result = list_files()

            # Send the tool result back to the LLM
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result)
            })

    # Ask the LLM to formulate its final answer
    final_response = client.chat.completions.create(
        model=os.getenv("OPENROUTER_MODEL"),
        messages=messages
    )

    print(final_response.choices[0].message.content)

else:
    print("LLM response:", message.content)