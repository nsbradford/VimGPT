import logging
import os
from typing import Dict, List

import litellm

# import openai

#=========================================================================
# TODO promptlayer is not working, have tried a few variations

# this was the old code before litellm:
# import promptlayer
# promptlayer.api_key = os.environ.get("PROMPTLAYER_API_KEY")
# openai = promptlayer.openai  # type: ignore

litellm.success_callback = ["promptlayer"]


#=========================================================================
# TODO, helicone cache is NOT working.
litellm.api_url = "https://oai.hconeai.com/v1"

litellm.headers = {
    "Helicone-Auth": f"Bearer {os.getenv('HELICONE_API_KEY')}",
    "Helicone-Cache-Enabled": "true",
}

logger = logging.getLogger(__name__)

def llm_get_keystrokes(model: str, messages: List[Dict[str, str]]) -> str:
    logger.warning(f"Calling LLM {model}")

    # this was the old code before litellm:
    # chat_completion = openai.ChatCompletion.create(
    #     model="gpt-4",
    #     temperature=0,
    #     messages=messages,
    #     api_key=os.environ["OPENAI_API_KEY"],
    #     api_base="https://oai.hconeai.com/v1",
    #     headers={
    #         "Helicone-Auth": f"Bearer {os.environ['HELICONE_API_KEY']}",
    #         "Helicone-Cache-Enabled": "true",
    #     },
    # )
    # text = chat_completion.choices[0].message.content
    # logger.warning(f"LLM response: {text}")
    
    litellm_completion = litellm.completion(model=model, messages=messages, temperature=0)
    text = litellm_completion.choices[0].message.content
    logger.warning(f"LiteLLM response: {litellm_completion.choices[0].message.content}")
    return text
