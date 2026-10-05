import argparse
import os
import sys
import json

from openai import OpenAI

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = os.getenv("OPENROUTER_BASE_URL", default="https://openrouter.ai/api/v1")

MODEL = os.getenv("MODEL", default="anthropic/claude-haiku-4.5")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", required=True)
    args = parser.parse_args()

    read_file = {
        "type": "function",
        "function": {
            "name": "Read",
            "description": "Read and return the contents of a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The path to the file to read"
                    }
                },
                "required": ["file_path"]
            }
        }
    }

    write = {
        "type": "function",
        "function": {
            "name": "Write",
            "description": "Write content to a file",
            "parameters": {
                "type": "object",
                "required": ["file_path", "content"],
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The path of the file to write to"
                    },
                "content": {
                    "type": "string",
                    "description": "The content to write to the file"
                    }
                }
            }
        }
    }

    if not API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is not set")

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!", file=sys.stderr)

    messages=[{"role": "user", "content": args.p}]

    # Agent Loop
    while True:
        chat = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=[read_file, write]
        )

        if not chat.choices or len(chat.choices) == 0:
            raise RuntimeError("no choices in response")

        message = chat.choices[0].message

        if not message.tool_calls:
            print(message.content)
            break
        
        messages.append(message)
        
        for tool in message.tool_calls:
            if tool.function.name == "Read":
                tool_args = json.loads(tool.function.arguments)
                with open(tool_args["file_path"], "r", encoding="utf-8") as file:
                    file_content = file.read()
                
                messages.append({"role" : "tool", "tool_call_id" : tool.id, "content" : file_content})

            elif tool.function.name == "Write":
                tool_args = json.loads(tool.function.arguments)
                with open(tool_args["file_path"], "w", encoding="utf-8") as file:
                    file.write(tool_args["content"])

                messages.append({"role" : "tool", "tool_call_id" : tool.id, "content" : tool_args["content"]})

if __name__ == "__main__":
    main()
