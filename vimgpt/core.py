# import logging
import logging
import time
from typing import List, Optional

import pynvim

from vimgpt.llm import llm_get_keystrokes
from vimgpt.prompts import PROMPT_VIM_GPT
from vimgpt.utils import extract_cmd_content, render_text

logger = logging.getLogger(__name__)


def vimgpt_agent(
        *, # force kwargs
    command: str,
    content: str,
    file_path: Optional[str],
    socket: Optional[str],
    max_calls: int = 1000,
    delay_seconds: Optional[int] = None,
) -> str:
    def get_vim():
        return (
            pynvim.attach("socket", path=socket)
            if socket
            else pynvim.attach("child", argv=["nvim", "--embed", "--headless"])
        )

    prompt = PROMPT_VIM_GPT(command)
    history: List[str] = []
    with get_vim() as nvim:
        nvim.command("setlocal buftype=nofile")
        nvim.command("set number")
        nvim.current.buffer[:] = content.split("\n")
        for _ in range(max_calls):
            buf = "\n".join(nvim.current.buffer[:])
            rendered = render_text(file_path, buf, nvim.current.window.cursor, history)
            raw_llm_text = llm_get_keystrokes(
                [
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": rendered},
                ]
            )
            cmd = extract_cmd_content(raw_llm_text)
            logger.info(f"VimGPT calling cmd: {cmd}")
            history.append(cmd)
            # this gets the command to show up in the UI
            nvim.command(f'echom "{cmd}"')
            if cmd == "wq":
                break
            else:
                nvim.command(cmd)
                if delay_seconds:
                    # useful for demos/debugging
                    time.sleep(delay_seconds)

        logger.info("VimGPT exited vim.")
        return buf
