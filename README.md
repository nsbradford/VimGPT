# VimGPT
Prototype LLM agent with direct Vim access, using [neovim/pynvim](https://github.com/neovim/pynvim).

## Why?
There are two common options for using LLM agents to edit files:
1. **Rewrite the entire file**: reliable, but very expensive (in time and tokens), and for small changes/big files it is incredibly wasteful and difficult to interpret where the change was made.
2. **Make a patch**: using a patch format such as [UDF](https://en.wikipedia.org/wiki/Diff) can make edits much faster and more clear, but is highly error-prone as the current generation of LLMs often make mistakes with line numbers, leading spaces, capitalization, etc.

**The Solution**: Instead of asking the agent to call a tool with the new contents, give the agent an "Editor" tool which drops into a sub-agent with appropriate context. The simulated editor shows the state of the editor in plaintext, takes individual keystrokes, and reflects updates. This can be conceptualized as individual keystrokes forming tools. And why invent your own when Vim already exists?

### Drawbacks
- This tends to be quite fast, but does consume a lot of requests because each command is its own request.
- GPT-3.5 struggles with doing things logically in Vim, so you are limited to GPT-4. (Claude-2.0 untested so far).

## Installation
TODO, will be
```bash
brew install neovim
pip install vimgpt
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

(Deprecated) Old version using pyenv/virtualenv
```bash
pyenv install 3.11:latest
pyenv virtualenv 3.11 k-llm
pyenv activate k-llm
pip install -r requirements.txt
```

### Demo
First make sure it's installed
```bash
poetry shell
poetry install
```


To run with headless vim:
```bash
vimgpt_demo_headless
```

To attach to a running Neovim instance so you can view what's happening in real-time as the agent does:
```bash
NVIM_LISTEN_ADDRESS=/tmp/nvimsocket nvim

# in separate terminal
vimgpt_demo_attached
```

### Publish to PyPI
To update the package on PyPI (https://pypi.org/project/vimgpt):

```bash
poetry build
poetry config pypi-token.pypi <YOUR_PYPI_TOKEN> # if it's your first time
poetry publish
```

### Linting and Formatting
Use ruff + black.

```bash
black .
ruff check . --fix
```

## Roadmap
- pyargs
- in-memory vs file system options
- test on multi-page files
- Cool demo