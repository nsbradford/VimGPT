import time
from typing import Callable

from vimgpt.llm import llm_get_keystrokes
from vimgpt.utils import extract_cmd_content, render_text


def vim_gpt(
    get_vim: Callable,
    filename: str,
    content: str,
    prompt: str,
    max_calls: int = 100,
    delay_seconds: int = 0,
):
    history = []

    with get_vim() as nvim:
        nvim.command("setlocal buftype=nofile")
        nvim.command("set number")
        nvim.current.buffer[:] = content.split("\n")
        for i in range(max_calls):
            buf = "\n".join(nvim.current.buffer[:])
            rendered = render_text(filename, buf, nvim.current.window.cursor, history)
            print(f"Current state at iteration {i}:\n{rendered}")
            raw_llm_text = llm_get_keystrokes(
                [
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": rendered},
                ]
            )
            cmd = extract_cmd_content(raw_llm_text)
            print(f'LLM calling cmd: "{cmd}"')
            history.append(cmd)
            nvim.command(f'echom "{cmd}"')
            if cmd == "wq":
                break
            else:
                # this gets the command to show up in the UI
                nvim.command(cmd)
                # Wait for a few seconds so you can capture the action (for screen recording)
                if delay_seconds > 0:
                    time.sleep(delay_seconds)

        final = render_text(filename, buf, nvim.current.window.cursor, history)
        print(f"LLM exited vim. Final state:\n{final}")
        return buf
