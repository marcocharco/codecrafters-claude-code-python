import os
import shlex
import subprocess
import yaml


def get_tools() -> list[dict]:
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


def get_skills(skills_dir) -> list[dict]:
    skills = []

    if skills_dir.exists():
        for dir in skills_dir.iterdir():
            if dir.is_dir():
                skill_path = dir / "SKILL.md"
                skill_content = skill_path.read_text(encoding="utf-8")

                frontmatter_raw = skill_content.split("---")[1]
                frontmatter = yaml.safe_load(frontmatter_raw)

                skills.append(
                    {
                        "name": frontmatter["name"],
                        "description": frontmatter["description"],
                    }
                )

    return skills


def get_skill_body(skills_dir, skill_name) -> str:
    skill_path = skills_dir / skill_name / "SKILL.md"
    if not skill_path.exists():
        return ""

    skill_content = skill_path.read_text(encoding="utf-8")
    skill_body = skill_content.split("---", 2)[2]

    return skill_body


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

    return result.stdout + result.stderr
