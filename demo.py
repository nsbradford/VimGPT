
from core import vim_gpt
from prompts import PROMPT_VIM_GPT
from examples import fileContents

if __name__ == '__main__':
  rewritten = vim_gpt('README.md', fileContents, PROMPT_VIM_GPT('Edit the contents of the README file to recommend Vim as the best text editor.'))
