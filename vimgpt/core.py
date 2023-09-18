import logging
import time
from typing import List, Optional

import pynvim

from vimgpt.llm import llm_get_keystrokes
from vimgpt.prompts import PROMPT_VIM_GPT
from vimgpt.utils import extract_cmd_contents, render_history, render_text

logger = logging.getLogger(__name__)


def vimgpt_agent(
    command: str,
    *,  # force kwargs
    original_content: str = "",
    file_path: Optional[str] = None,
    socket: Optional[str] = None,
    max_calls: int = 1000,
    delay_seconds: Optional[int] = None,
    model: str = "gpt-4",
    multicommand_enabled: bool = False,
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
    - model (str, optional): The specific model to be used. Default is 'gpt-4'.

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
        # nvim.command("set number")
        nvim.command("set relativenumber")
        # highlighting just for demo purposes
        if file_path and file_path.endswith(".py"):
            nvim.command(":setfiletype python")
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
            logger.info(f"VimGPT received cmds: {cmds}")
            for i, cmd in enumerate(cmds):
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
                    if i == 0:
                        logger.warning("VimGPT decided to exit.")
                        return buf
                    else:
                        logger.info(
                            "VimGPT tried to exit, but we're forcing it to re-read the file to make sure it's done."
                        )
                        break

                # some commands just can't shake out of it with prompts.
                elif cmd.lower() in set(
                    [
                        "normal <esc>",
                    ]
                ):
                    logger.info(f"Skipping bad command: '{cmd}'")
                else:
                    logger.warning(f"VimGPT calling cmd: {cmd}")
                    history.append(cmd)
                    try:
                        # this gets the command to show up in the UI
                        nvim.command(f'echom "{cmd}"')
                        # need to escape quotes and some other chars
                        nvim.command(cmd.replace('"', r"\""))
                    except pynvim.api.nvim.NvimError as e:
                        # if there's an error, we want to short-circuit
                        logger.warning(f"VimGPT Error on command '{cmd}': {e}")
                        history.append(f"\nError on command '{cmd}': {e}\n")
                        break
                    if delay_seconds:
                        # useful for demos/debugging
                        time.sleep(delay_seconds)

                if not multicommand_enabled:
                    break

        logger.warning(f"VimGPT reached max calls of {max_calls}.")
        return buf
