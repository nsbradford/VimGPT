# VimGPT
Prototype LLM agent with direct Vim access, using [neovim/pynvim](https://github.com/neovim/pynvim).

![PyPI - Version](https://img.shields.io/pypi/v/vimgpt)
![GitHub Workflow Status (with event)](https://img.shields.io/github/actions/workflow/status/nsbradford/vimgpt/main.yml?label=CI%20tests)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![X (formerly Twitter) Follow](https://img.shields.io/twitter/follow/n_s_bradford)](https://twitter.com/n_s_bradford)


## Why?
There are two common options for using LLM agents to edit files:
1. **Rewrite the entire file**: reliable, but very expensive (in time and tokens), and for small changes/big files it is incredibly wasteful and difficult to interpret where the change was made.
2. **Make a patch**: using a patch format such as [UDF](https://en.wikipedia.org/wiki/Diff) can make edits much faster and more clear, but is highly error-prone as the current generation of LLMs often make mistakes with line numbers, leading spaces, capitalization, etc.

**The Solution**: Instead of asking the agent to call a tool with the new contents, give the agent an "Editor" tool which drops into a sub-agent with appropriate context. The simulated editor shows the state of the editor in plaintext, takes individual keystrokes, and reflects updates. This can be conceptualized as individual keystrokes forming tools. And why invent your own when Vim already exists?

### Drawbacks
- This tends to be quite fast, but does consume a lot of requests because each command is its own request.
- GPT-3.5 struggles with doing things logically in Vim, so you are limited to GPT-4. (Claude-2.0 untested so far).

## Installation

You'll need to [install neovim](https://github.com/neovim/neovim/wiki/Installing-Neovim), if you're on MacOS you can simply `brew install neovim`. Then:

```bash
pip install vimgpt # or poetry add vimgpt
```

## Usage

### As a CLI / Demo

CLI usage (intended to demo/test):
```
$ vimgpt [-h] [--socket SOCKET] [--verbose] filepath command

VimGPT Entry Point

positional arguments:
  filepath              File for VimGPT to open.
  command               Task for VimGPT to perform on the file.

options:
  -h, --help            show this help message and exit
  --socket SOCKET, -s SOCKET
                        Path to nvim socket of running nvim process. If left empty, VimGPT will run in
                        headless mode. Suggested value: '/tmp/nvimsocket'.
  --verbose, -v         Sets logging level to debug.
```

To run with headless vim:
```bash
vimgpt tests/samples/README.md "Edit the contents of the README file to recommend Vim as the best text editor."
```

To attach to a running Neovim instance so you can view what's happening in real-time as the agent does:
```bash
NVIM_LISTEN_ADDRESS=/tmp/nvimsocket nvim

# in separate terminal
vimgpt --socket '/tmp/nvimsocket' tests/samples/README.md "Edit the contents of the README file to recommend Vim as the best text editor."
```

### As a library

```python
from vimgpt import exec_vimgpt 

exec_vimgpt(get_vim, args.filepath, contents, PROMPT_VIM_GPT(args.command))

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

### Linting, Formatting, Typechecking
Use ruff + black + mypy.

```bash
black .
ruff check . --fix
mypy vimgpt
```

## Roadmap
- Open issues
  - sometimes gets confused and will enter infinite loops because of the current naive approach to history, `$ vimgpt --socket '/tmp/nvimsocket' tests/samples/README.md "Edit to recommend vim instead of emacs."`
- in-memory vs file system options
- pyargs
- test on multi-page files
- Cool demo