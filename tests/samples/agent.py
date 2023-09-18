from typing import List, Optional, Tuple

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

from vimgpt.prompts import PROMPT_VIM_GPT, PROMPT_VIM_GPT_TOOL
from vimgpt.utils import add_line_numbers


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


def vimgpt_agent(
    command: str,
    *,
    original_content: str = "",
    file_path: Optional[str] = None,
    socket: Optional[str] = None,
    max_calls: int = 1000,
    delay_seconds: Optional[int] = None,
    model: str = "gpt-4",
) -> str:
    def get_vim():
        return (
            pynvim.attach("socket", path=socket)
            if socket
            else pynvim.attach("child", argv=["nvim", "--embed", "--headless"])
        )

    prompt = PROMPT_VIM_GPT(command)
    with get_vim() as nvim:
        for _ in range(max_calls):
            buf = "\n".join(nvim.current.buffer[:])
            rendered = render_text(file_path, buf, nvim.current.window.cursor)
            messages = [
                {"role": "system", "content": prompt},
                {
                    "role": "user",
                    "content": rendered,
                },
            ]
            cmds = completion(
                model,
                messages,
            )
            for cmd in cmds:
                nvim.command(cmd)
        return buf


def insert_cursor(text, rowOneIdx, col):
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


def vimgpt_agent_plan_and_execute(
    *,
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
            nvim.command(f'echom "{cmd}"')
            nvim.command(cmd)
            buf = "\n".join(nvim.current.buffer[:])
            rendered = render_text(file_path, buf, nvim.current.window.cursor)
            return rendered

        tools: List[BaseTool] = [
            Tool(name="vim_cmd", func=exec_vim, description=PROMPT_VIM_GPT_TOOL),
        ]
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
            nvim.command(f'echom "{cmd}"')
            nvim.command(cmd)
            buf = "\n".join(nvim.current.buffer[:])
            rendered = render_text(file_path, buf, nvim.current.window.cursor)
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
