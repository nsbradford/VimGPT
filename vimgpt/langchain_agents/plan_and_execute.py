# we don't want this package to depend on langchain.
# type: ignore

import logging
from typing import List, Optional

import promptlayer  # noqa: F401 # Don't forget this - see docs
import pynvim
from langchain.agents.tools import BaseTool, Tool
from langchain.callbacks import PromptLayerCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain_experimental.plan_and_execute import (
    PlanAndExecute,
    load_agent_executor,
    load_chat_planner,
)

from vimgpt.prompts import PROMPT_VIM_GPT_TOOL
from vimgpt.utils import render_text

logger = logging.getLogger(__name__)


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
