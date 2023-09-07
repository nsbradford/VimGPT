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

brew install poetry # typical install methods didn't work for me
poetry install
```

## Demo
To run with headless vim:
```bash
python demo_headless.py
```

To attach to a running Neovim instance so you can view what's happening in real-time as the agent does:
```bash
NVIM_LISTEN_ADDRESS=/tmp/nvimsocket nvim

# in separate terminal
python demo_attached.py
```

## Roadmap
- pyargs
- in-memory vs file system options
- test on multi-page files
- Cool demo
- CI
- deploy on PyPI