import os
import shlex
import subprocess


def get_tools():
    tools = [
        {
            "type": "function",
            "function": {
                "name": "Read",
                "description": "Read and return the contents of a file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "The path to the file to read",
                        }
                    },
                    "required": ["file_path"],
                },
            },
        },
        {
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
                            "description": "The path of the file to write to",
                        },
                        "content": {
                            "type": "string",
                            "description": "The content to write to the file",
                        },
                    },
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "Bash",
                "description": "Execute a shell command",
                "parameters": {
                    "type": "object",
                    "required": ["command"],
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "The command to execute",
                        }
                    },
                },
            },
        },
    ]

    return tools


def read_file(file_path: str) -> str:

    with open(file_path) as file:
        file_content = file.read()

    return file_content


def write_file(file_path: str, content: str) -> str:
    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
    with open(file_path, "w") as file:
        file.write(content)

    return "Successfully written to file"


def bash(command: str) -> str:

    result = subprocess.run(
        shlex.split(command), capture_output=True, text=True, check=False
    )

    return result.stdout if result.stdout else result.stderr


# def get_skills:
#     skills = [
#
#     ]
#     return skills
