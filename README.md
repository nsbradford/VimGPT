# VimGPT
Prototype LLM agent with direct Vim access, using [neovim/pynvim](https://github.com/neovim/pynvim).

![GitHub Workflow Status (with event)](https://img.shields.io/github/actions/workflow/status/nsbradford/vimgpt/main.yml?label=CI%20tests)
![PyPI - Version](https://img.shields.io/pypi/v/vimgpt)
![PyPI - Downloads](https://img.shields.io/pypi/dm/vimgpt)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![X (formerly Twitter) Follow](https://img.shields.io/twitter/follow/n_s_bradford)](https://twitter.com/n_s_bradford)

Built with:
- [LiteLLM](https://github.com/BerriAI/litellm) for LLM client interop
- [Promptlayer](https://promptlayer.com/) for observability
- [Helicone](https://www.helicone.ai/) for caching

## Why?
There are two common options for using LLM agents to edit files:
1. **Rewrite the entire file**: reliable, but very expensive (in time and tokens), and for small changes/big files it is incredibly wasteful and difficult to interpret where the change was made. Also, what if you want to make a 1-line change to a million-line file that won't fit in the context window?
2. **Make a patch**: using a patch format such as [UDF](https://en.wikipedia.org/wiki/Diff) can make edits much faster and more clear, but is highly error-prone as the current generation of LLMs often make mistakes with line numbers, leading spaces, capitalization, etc.
3. **Roll your own editor**: this can work pretty well, but 1) the models don't have training data on your custom format, and 2) now you're maintaining a custom format.

**The Solution**: Instead of asking the agent to call a tool with the new contents, give the agent a "Editor" tool which drops into a sub-agent with appropriate context. The simulated editor shows the state of the editor in plaintext, takes individual keystrokes, and reflects updates. And why invent your own editor when LLMs already know about Vim?

### Drawbacks
- VimGPT's performance varies considerably depending on your chosen agent runtime, as the central challenge is managing history and intention while chaining many commands.
- VimGPT tends to be quite fast, but does consume a lot of requests because each command is its own request.

## Installation

You'll need to [install neovim](https://github.com/neovim/neovim/wiki/Installing-Neovim), if you're on MacOS you can simply `brew install neovim`. Then [install from PyPI](https://pypi.org/project/vimgpt/):

```bash
pip install vimgpt # or poetry add vimgpt
```

## Usage

### As a CLI / Demo

CLI usage (intended to demo/test):

```
$ vimgpt --help                      
usage: vimgpt [-h] [--path PATH] [--output [OUTPUT]] [--socket SOCKET] [--loglevel {DEBUG,INFO,WARNING}] [--max-calls MAX_CALLS] [--delay-seconds DELAY_SECONDS] command

VimGPT CLI

positional arguments:
  command               Task for VimGPT to perform on the file, in natural language: 
                        'Rename Bob to Bill in paragraph 2`, 
                        'make arg `user` optional on line 34', 
                        'rewrite this in iambic pentameter', etc.

options:
  -h, --help            show this help message and exit
  --path PATH, -p PATH  File for VimGPT to open. 
                        NOTE: for safety, VimGPT will NOT make changes directly
                        to the file unless the --output flag is provided.
  --output [OUTPUT], -o [OUTPUT]
                        Specify output file. If flag is not provided, 
                        VimGPT will NOT make changes directly to the file. 
                        If flag is provided without value, uses the same path as the input file. 
                        If flag is provided with no value and there is no input file specified, 
                        will output to 'vimgpt_output.txt'.
  --socket SOCKET, -s SOCKET
                        Path to nvim socket of running nvim process. 
                        If left empty, VimGPT will run in headless mode.
                        Suggested value: '/tmp/nvimsocket'.
  --loglevel {DEBUG,INFO,WARNING}
                        Set the logging level (default: WARNING)
  --max-calls MAX_CALLS
                        Maximum number of LLM calls. Default is 1000.
  --delay-seconds DELAY_SECONDS
                        Delay in seconds. If not provided, defaults to None.
```

To run with headless vim:
```bash
vimgpt "Edit the contents of the README file to recommend Vim as the best text editor." --path tests/samples/README.md --loglevel INFO
```

To attach to a running Neovim instance so you can view what's happening in real-time as the agent does:
```bash
NVIM_LISTEN_ADDRESS=/tmp/nvimsocket nvim

# in separate terminal
vimgpt "Edit the contents of the README file to recommend Vim as the best text editor." --path tests/samples/README.md --loglevel INFO --socket '/tmp/nvimsocket' 
```

### As a library

```python
from vimgpt import vimgpt_agent 

original_file_content: str = '???'

new_file_content: str = vimgpt_agent(
    command='Edit to recommend vim over emacs.',
    content=original_file_content,
    file_path='does_not_matter_just_useful_for_prompt.md',
    # socket=None, # or '/path/to/running/nvim'
    # max_calls=1000, # can use prevent cycles
    # delay_seconds=2, # if you want to follow in real-time more easily
)

```


## Development
This project uses [poetry](https://python-poetry.org/).

```bash
# If you don't already have 3.11 installed
pyenv install 3.11:latest

# typical poetry install methods didn't work for me
brew install poetry 

# this will create a .venv in the project directory.
# it should automatically check the right version is installed.
poetry install

# view info about your new venv
poetry env list
```


### Publish to PyPI
To update the package on PyPI (https://pypi.org/project/vimgpt):
```bash
poetry build
poetry config pypi-token.pypi YOUR_PYPI_TOKEN
poetry publish
```

### Linting, Formatting, Typechecking, Testing
Use ruff + black + mypy + pytest. If you're using VSCode, you might want to follow [these instructions](https://scottlarsen.com/2021/06/17/mypy-pyenv-issue-in-VSCode.html) to make sure the mypy extension settings are set to use your active interpreter (the poetry venv).

```bash
black .
ruff check . --fix
mypy vimgpt
pytest -vv -s --verbose
```

## Roadmap
- turn into langchain tool/agent
  - integrate promptlayer
  - Abstract over LLM provider
- Multi-line
  - test
  - Fix relative line numbers
- More examples
  - improve the basic demo
  - Regex search and replace
  - test on multi-page files
  - Demo video
  - Call it WITHIN neovim itself while you're working on something
- Async/await instead of blocking (at least for LLM calls - does pynvim support?)
- Open issues
  - sometimes gets confused and will enter infinite loops because of the current naive approach to history, `$ vimgpt --socket '/tmp/nvimsocket' tests/samples/README.md "Edit to recommend vim instead of emacs."`
  - cursor representation (suggested by GPT-4) likely causes some problems/could be optimized. A simple inserted `_` or `|` might work.