import pynvim
from core import vim_gpt
from examples import fileContents
from prompts import PROMPT_VIM_GPT


def get_vim():
    return pynvim.attach("socket", path="/tmp/nvimsocket")


if __name__ == "__main__":
    rewritten = vim_gpt(
        get_vim,
        "README.md",
        fileContents,
        PROMPT_VIM_GPT(
            "Edit the contents of the README file to recommend Vim as the best text editor."
        ),
        delay_seconds=2,
    )
