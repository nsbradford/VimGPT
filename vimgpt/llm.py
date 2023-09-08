import os
from typing import Dict, List

import openai


def llm_get_keystrokes(messages: List[Dict[str, str]]) -> str:
    chat_completion = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        api_key=os.environ["OPENAI_API_KEY"],
        api_base="https://oai.hconeai.com/v1",
        headers={
            "Helicone-Auth": f"Bearer {os.environ['HELICONE_API_KEY']}",
            "Helicone-Cache-Enabled": "true",
        },
    )
    return chat_completion.choices[0].message.content
