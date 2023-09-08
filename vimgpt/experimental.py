# import logging
import logging
from typing import List, Optional

import pynvim
from langchain.agents.tools import BaseTool, Tool
from langchain.chat_models import ChatOpenAI
from langchain_experimental.plan_and_execute import (
    PlanAndExecute,
    load_agent_executor,
    load_chat_planner,
)

from vimgpt.prompts import PROMPT_VIM_GPT_TOOL
from vimgpt.utils import render_text

logger = logging.getLogger(__name__)


def vimgpt_agent_langchain(
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
        model = ChatOpenAI(temperature=0)
        planner = load_chat_planner(model)
        executor = load_agent_executor(model, tools, verbose=True)
        agent = PlanAndExecute(planner=planner, executor=executor, verbose=True)
        agent.run(command)
        return "\n".join(nvim.current.buffer[:])
