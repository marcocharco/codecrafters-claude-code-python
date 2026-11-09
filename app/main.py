import argparse
import json
import os
import sys
from pathlib import Path

from openai import OpenAI

from .utils import bash, get_skill_body, get_skills, get_tools, read_file, write_file

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

    if not API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is not set")

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!", file=sys.stderr)

    skills = get_skills(Path(".claude/skills"))
    system_prompt = "You have access to the following skills:\n"
    for skill in skills:
        system_prompt += f"- {skill['name']}: {skill['description']}\n"

    if args.p.startswith("/"):
        skill_name = args.p.split(" ")[0].strip("/")
        body = get_skill_body(Path(".claude/skills"), skill_name)
        user_prompt = body if body else args.p
    else:
        user_prompt = args.p

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    # Agent Loop
    while True:
        chat = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=get_tools(),
            max_tokens=4096,
        )

        if not chat.choices or len(chat.choices) == 0:
            raise RuntimeError("no choices in response")

        message = chat.choices[0].message

        if not message.tool_calls:
            print(message.content)
            break

        messages.append(message)

        for tool in message.tool_calls:
            tool_args = json.loads(tool.function.arguments)
            tool_message = {"role": "tool", "tool_call_id": tool.id, "content": ""}
            if tool.function.name == "Read":
                tool_message["content"] = read_file(tool_args["file_path"])

            elif tool.function.name == "Write":
                tool_message["content"] = write_file(
                    tool_args["file_path"], tool_args["content"]
                )

            elif tool.function.name == "Bash":
                tool_message["content"] = bash(tool_args["command"])

            messages.append(tool_message)


if __name__ == "__main__":
    main()
