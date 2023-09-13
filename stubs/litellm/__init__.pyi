from .testing import *
from .main import *
from .integrations import *
import threading
from .timeout import timeout as timeout
from .utils import (
    client as client,
    completion_cost as completion_cost,
    cost_per_token as cost_per_token,
    exception_type as exception_type,
    get_litellm_params as get_litellm_params,
    get_optional_params as get_optional_params,
    logging as logging,
    modify_integration as modify_integration,
    token_counter as token_counter,
    ModelResponse as ModelResponse,
)
from _typeshed import Incomplete
from openai.error import (
    AuthenticationError as AuthenticationError,
    InvalidRequestError as InvalidRequestError,
    OpenAIError as OpenAIError,
    RateLimitError as RateLimitError,
    ServiceUnavailableError as ServiceUnavailableError,
)

success_callback: Incomplete
failure_callback: Incomplete
set_verbose: bool
telemetry: bool
max_tokens: int
retry: bool
api_key: Incomplete
openai_key: Incomplete
azure_key: Incomplete
anthropic_key: Incomplete
replicate_key: Incomplete
cohere_key: Incomplete
openrouter_key: Incomplete
huggingface_key: Incomplete
vertex_project: Incomplete
vertex_location: Incomplete
caching: bool
hugging_api_token: Incomplete
togetherai_api_key: Incomplete
model_cost: Incomplete

class MyLocal(threading.local):
    user: str
    def __init__(self) -> None: ...

def identify(event_details) -> None: ...

api_base: Incomplete
headers: Incomplete
api_version: Incomplete
organization: Incomplete
config_path: Incomplete
secret_manager_client: Incomplete
open_ai_chat_completion_models: Incomplete
open_ai_text_completion_models: Incomplete
cohere_models: Incomplete
anthropic_models: Incomplete
replicate_models: Incomplete
openrouter_models: Incomplete
vertex_chat_models: Incomplete
vertex_text_models: Incomplete
huggingface_models: Incomplete
ai21_models: Incomplete
model_list: Incomplete
provider_list: Incomplete
open_ai_embedding_models: Incomplete

def completion(
    model,
    messages,  # required params
    # Optional OpenAI params: see https://platform.openai.com/docs/api-reference/chat/create
    functions=[],
    function_call="",  # optional params
    temperature=1,
    top_p=1,
    n=1,
    stream=False,
    stop=None,
    max_tokens=float("inf"),
    presence_penalty=0,
    frequency_penalty=0,
    logit_bias={},
    user="",
    deployment_id=None,
    # Optional liteLLM function params
    *,
    return_async=False,
    api_key=None,
    force_timeout=600,
    logger_fn=None,
    verbose=False,
    azure=False,
    custom_llm_provider=None,
    custom_api_base=None,
    # model specific optional params
    # used by text-bison only
    top_k=40,
    request_timeout=0,  # unused var for old version of OpenAI API
) -> ModelResponse: ...
