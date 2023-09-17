import logging
import os
from typing import Dict, List

import litellm
from litellm import completion

# https://docs.litellm.ai/docs/observability/promptlayer_integration
litellm.success_callback = ["promptlayer"]

# https://docs.helicone.ai/getting-started/integration-method/litellm
litellm.api_base = "https://oai.hconeai.com/v1"
litellm.headers = {
    "Helicone-Auth": f"Bearer {os.getenv('HELICONE_API_KEY')}",
    "Helicone-Cache-Enabled": "true",
}

logger = logging.getLogger(__name__)


def llm_get_keystrokes(model: str, messages: List[Dict[str, str]]) -> str:
    logger.info(f"Calling LLM {model}")
    litellm_completion = completion(model=model, messages=messages, temperature=0)
    text = litellm_completion.choices[0].message.content
    logger.info(f"LiteLLM response: {litellm_completion.choices[0].message.content}")
    return text
