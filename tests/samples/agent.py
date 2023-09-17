import logging
import os
import re
import time
from typing import Dict, List, Optional, Tuple

import litellm
import promptlayer  # noqa: F401 # Don't forget this - see docs
import pynvim
from langchain.agents import AgentType, initialize_agent
from langchain.agents.tools import BaseTool, Tool
from langchain.callbacks import PromptLayerCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain_experimental.plan_and_execute import (
    PlanAndExecute,
    load_agent_executor,
    load_chat_planner,
)
from litellm import completion

logger = logging.getLogger(__name__)

# https://docs.litellm.ai/docs/observability/promptlayer_integration
litellm.success_callback = ["promptlayer"]

# https://docs.helicone.ai/getting-started/integration-method/litellm
litellm.api_base = "https://oai.hconeai.com/v1"
litellm.headers = {
    "Helicone-Auth": f"Bearer {os.getenv('HELICONE_API_KEY')}",
    "Helicone-Cache-Enabled": "true",
}

logger = logging.getLogger(__name__)



def extract_cmd_contents(s) -> List[str]:
    pattern = r"<cmd>(.*?)</cmd>"
    matches = re.findall(
        pattern, s, re.DOTALL
    )  # re.DOTALL makes . match newlines as well
    return matches if matches else [s]


def add_line_numbers(text):
    lines = text.split("\n")
    return "\n".join([f"{idx}:{line}" for idx, line in enumerate(lines, 1)])


def render_history(history: List[str]):
    return "\n".join([f"<cmd>{cmd}</cmd>" for cmd in history])


def render_text(
    file_path: Optional[str],
    text: str,
    cursor: Tuple[int, int],
):
    (rowOneIdx, colOneIdx) = cursor
    # insert the cursor, then add line numbers.
    lines = text.split("\n")
    cols = len(lines[rowOneIdx - 1])
    with_cursor = insert_cursor(text, rowOneIdx, colOneIdx)
    with_line_numbers = add_line_numbers(with_cursor)
    filename = file_path or ""
    filewrapped = f"```{filename}\n{with_line_numbers}\n```"
    postfix = f"\nCol {colOneIdx} of {cols}; Line {rowOneIdx} of {len(lines)};\n"
    return filewrapped + postfix


def insert_cursor(text, rowOneIdx, col):
    """
    Rows are one-indexed, columns are zero-indexed
    """
    row = rowOneIdx - 1
    # Split the text into rows
    rows = text.split("\n")

    # Ensure valid row and col
    if row < 0 or row >= len(rows):
        raise ValueError("Invalid row.")
    if col < 0 or col > len(rows[row]):
        raise ValueError("Invalid column.")

    # Calculate position to insert cursor; +1 accounts for newline characters
    pos = sum(len(r) + 1 for r in rows[:row]) + col + 1

    # Insert the combining low line character at the determined position
    return text[:pos] + "\u0332" + text[pos:]



def llm_get_keystrokes(model: str, messages: List[Dict[str, str]]) -> str:
    logger.warning(f"Calling LLM {model}")
    litellm_completion = completion(model=model, messages=messages, temperature=0)
    text = litellm_completion.choices[0].message.content
    logger.warning(f"LiteLLM response: {litellm_completion.choices[0].message.content}")
    return text


def PROMPT_VIM_GPT(goal: str) -> str:
    """
    Removed <thoughts>CONCISE thoughts about what to do next</thoughts> tag for faster performance.
    """
    return (
        f"You are ThePrimeagen, a god-level software engineer and Vim user, with the following goal: \n<goal>\n{goal}\n</goal>"
        + """

RULES:
- You interact with the world through structured Vim commands, which will be routed through the Python package pynvim and executed via `nvim.command(<your command>)`.
- You must respond in this format with the EXACT text that should be given to `nvim.command()`. 
- Remember, if you are using a normal mode command, you must prefix your command with 'normal'. Remember, you must always use an argument if you use 'normal'.
- Do NOT use <Esc> to exit insert mode.
- Respond with ONLY <cmd> tag, do not provide any other comments or commentary.
- Remember, you will only be able to see the history of commands you have run, and the current file contents, so do not delete anything you need to remember.
- You are allowed to give multiple commands at once, as long as they are each in their own <cmd> tag.
- Use the MINIMUM number of keystrokes necessary. You want to be as efficient as possible.

<cmd>The exact text that should be given to `nvim.command()`</cmd>

Examples:
- Enter insert mode: <cmd>normal i</cmd>
- Enter insert mode and write text: <cmd>normal iHello, world!</cmd>
- Start search for "pattern": <cmd>/pattern</cmd>
- Delete a line: <cmd>normal dd</cmd>
- Move cursor to start of 11th line: <cmd>normal 7G</cmd>

When you are finished, close the session with "wq" command.
<cmd>wq</cmd>

Here is the file, which is already open in nvim:
"""
    )


PROMPT_VIM_GPT_TOOL = """
- You interact with the world through structured Vim commands, which will be routed through the Python package pynvim and executed via `nvim.command(<your command>)`.
- You must respond in this format with the EXACT text that should be given to `nvim.command()`. 
- Remember, if you are using a normal mode command, you must prefix your command with 'normal'. 

Examples:
- Enter insert mode: "normal i"
- Start search for "pattern": "/pattern"
- Delete a line: "normal dd"
- Move cursor to start of 11th line: "normal 7G"
"""


def vimgpt_agent(
    command: str,
    *,  # force kwargs
    original_content: str = "",
    file_path: Optional[str] = None,
    socket: Optional[str] = None,
    max_calls: int = 1000,
    delay_seconds: Optional[int] = None,
    model: str = "gpt-4",
) -> str:
    """
    Interface between Vim/Neovim and a GPT model to execute commands in the editor based on model suggestions.

    This function facilitates communication between Vim and a specified GPT model. Given an initial command,
    content, and other optional parameters, it guides the GPT model to produce appropriate Vim commands,
    which are then executed in the editor in real-time.

    Parameters:
    - command (str): The initial command to guide the GPT model's response.
    - original_content (str, optional): The initial content to be loaded into the Vim buffer. Default is an empty string.
    - file_path (str, optional): Path to the file being edited, if any. Default is None.
    - socket (str, optional): Path to a Neovim socket for attachment. If None, a new Neovim process is started. Default is None.
    - max_calls (int, optional): Maximum number of times the GPT model should be called. Default is 1000.
    - delay_seconds (int, optional): Time delay (in seconds) between successive Vim commands. Useful for demos/debugging. Default is None.
    - model (str, optional): The specific GPT model to be used. Default is 'gpt-4'.

    Returns:
    - str: The final state of the Vim buffer after all the commands have been executed.

    """

    def get_vim():
        return (
            pynvim.attach("socket", path=socket)
            if socket
            else pynvim.attach("child", argv=["nvim", "--embed", "--headless"])
        )

    prompt = PROMPT_VIM_GPT(command)
    history: List[str] = ["setlocal buftype=nofile", "set number"]
    with get_vim() as nvim:
        nvim.command("setlocal buftype=nofile")
        nvim.command("set number")
        nvim.current.buffer[:] = original_content.split("\n")
        for _ in range(max_calls):
            buf = "\n".join(nvim.current.buffer[:])
            messages = [{"role": "system", "content": prompt}]
            if original_content != "" and buf != original_content:
                messages.append(
                    {
                        "role": "user",
                        "content": render_text(file_path, original_content, (1, 0)),
                    },
                )
            messages.extend(
                [
                    {"role": "assistant", "content": render_history(history)},
                    {
                        "role": "user",
                        "content": render_text(
                            file_path, buf, nvim.current.window.cursor
                        ),
                    },
                ]
            )

            raw_llm_text = llm_get_keystrokes(
                model,
                messages,
            )
            cmds = extract_cmd_contents(raw_llm_text)
            logger.warning(f"VimGPT received cmds: {cmds}")
            for cmd in cmds:
                logger.warning(f"VimGPT calling cmd: {cmd}")
                history.append(cmd)
                # this gets the command to show up in the UI
                nvim.command(f'echom "{cmd}"')
                if cmd in set(
                    [
                        "q",
                        "q!",
                        "wq",
                        "wq!",
                        "w",
                        "w!",
                        ":q",
                        ":q!",
                        ":wq",
                        ":wq!",
                        ":w",
                        ":w!",
                    ]
                ):
                    logger.warning("VimGPT decided to exit.")
                    return buf
                else:
                    try:
                        nvim.command(cmd)
                    except pynvim.api.nvim.NvimError as e:
                        # if there's an error, we want to short-circuit
                        logger.warning(f"VimGPT Error on command '{cmd}': {e}")
                        history.append(f"\nError on command '{cmd}': {e}\n")
                        break
                    if delay_seconds:
                        # useful for demos/debugging
                        time.sleep(delay_seconds)

        logger.warning(f"VimGPT reached max calls of {max_calls}.")
        return buf


def vimgpt_agent_plan_and_execute(
    *,  # force kwargs
    command: str,
    content: str = "",
    file_path: Optional[str] = None,
    socket: Optional[str] = None,
    max_calls: int = 1000,
    delay_seconds: Optional[int] = None,
) -> str:
    def get_vim():
        return (
            pynvim.attach("socket", path=socket)
            if socket
            else pynvim.attach("child", argv=["nvim", "--embed", "--headless"])
        )

    with get_vim() as nvim:
        nvim.command("setlocal buftype=nofile")
        nvim.command("set number")
        nvim.current.buffer[:] = content.split("\n")

        def exec_vim(cmd: str):
            if cmd in set(
                [
                    "q",
                    "q!",
                    "wq",
                    "wq!",
                    "w",
                    "w!",
                    ":q",
                    ":q!",
                    ":wq",
                    ":wq!",
                    ":w",
                    ":w!",
                ]
            ):
                return "There is no need to save the file, it will be saved automatically with the current contents if you exit."
            # this gets the command to show up in the UI
            nvim.command(f'echom "{cmd}"')
            nvim.command(cmd)
            logger.warning(f"VimGPT calling cmd: {cmd}")
            buf = "\n".join(nvim.current.buffer[:])
            rendered = render_text(file_path, buf, nvim.current.window.cursor)
            logger.warning(f"VimGPT rendered: {rendered}")
            return rendered

        tools: List[BaseTool] = [
            Tool(name="vim_cmd", func=exec_vim, description=PROMPT_VIM_GPT_TOOL),
        ]

        # TODO caching not working for chat models?
        # https://discord.com/channels/1038097195422978059/1149840567895867443/1149840567895867443
        # openai.api_base = "https://oai.hconeai.com/v1"
        # , headers={"Helicone-Cache-Enabled": "true"}
        # model='gpt-4',
        model = ChatOpenAI(
            temperature=0, callbacks=[PromptLayerCallbackHandler(pl_tags=["langchain"])]
        )
        planner = load_chat_planner(model)
        executor = load_agent_executor(model, tools, verbose=True)
        agent = PlanAndExecute(planner=planner, executor=executor, verbose=True)
        agent.run(command)
        return "\n".join(nvim.current.buffer[:])


def vimgpt_agent_react(
    *,  # force kwargs
    command: str,
    agent_type: AgentType,
    content: str = "",
    file_path: Optional[str] = None,
    socket: Optional[str] = None,
    max_calls: int = 1000,
    delay_seconds: Optional[int] = None,
) -> str:
    def get_vim():
        return (
            pynvim.attach("socket", path=socket)
            if socket
            else pynvim.attach("child", argv=["nvim", "--embed", "--headless"])
        )

    with get_vim() as nvim:
        nvim.command("setlocal buftype=nofile")
        nvim.command("set number")
        nvim.current.buffer[:] = content.split("\n")

        def exec_vim(cmd: str):
            if cmd in set(
                [
                    "q",
                    "q!",
                    "wq",
                    "wq!",
                    "w",
                    "w!",
                    ":q",
                    ":q!",
                    ":wq",
                    ":wq!",
                    ":w",
                    ":w!",
                ]
            ):
                return "There is no need to save the file, it will be saved automatically with the current contents if you exit."
            # this gets the command to show up in the UI
            nvim.command(f'echom "{cmd}"')
            nvim.command(cmd)
            logger.warning(f"VimGPT calling cmd: {cmd}")
            buf = "\n".join(nvim.current.buffer[:])
            rendered = render_text(file_path, buf, nvim.current.window.cursor)
            logger.warning(f"VimGPT rendered: {rendered}")
            return rendered

        tools: List[BaseTool] = [
            Tool(name="vim_cmd", func=exec_vim, description=PROMPT_VIM_GPT_TOOL),
        ]

        # TODO caching not working for chat models?
        # https://discord.com/channels/1038097195422978059/1149840567895867443/1149840567895867443
        # openai.api_base = "https://oai.hconeai.com/v1"
        # , headers={"Helicone-Cache-Enabled": "true"}
        # model='gpt-4',
        model = ChatOpenAI(
            temperature=0, callbacks=[PromptLayerCallbackHandler(pl_tags=["langchain"])]
        )
        agent = initialize_agent(tools, model, agent=agent_type, verbose=True)
        agent.run(command)
        return "\n".join(nvim.current.buffer[:])
