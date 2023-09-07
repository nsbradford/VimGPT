
import pynvim
from .core import vim_gpt
from .prompts import PROMPT_VIM_GPT
from .examples import fileContents

def get_vim():
  return pynvim.attach('child', argv=["nvim", "--embed", "--headless"])

def main():
  rewritten = vim_gpt(get_vim, 'README.md', fileContents, PROMPT_VIM_GPT('Edit the contents of the README file to recommend Vim as the best text editor.'))

if __name__ == '__main__':
  main()
