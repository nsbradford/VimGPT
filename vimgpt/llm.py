import logging
import os
from typing import Dict, List

import promptlayer

logger = logging.getLogger(__name__)
promptlayer.api_key = os.environ.get("PROMPTLAYER_API_KEY")
openai = promptlayer.openai  # type: ignore


def llm_get_keystrokes(messages: List[Dict[str, str]]) -> str:
    logger.warning(f"Calling LLM with: {messages}")
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
    text = chat_completion.choices[0].message.content
    logger.warning(f"LLM response: {text}")
    return text
