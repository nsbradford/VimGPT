# KeyboardLLM
LLM agent tool for interacting with files via keystrokes.

## Why KeyboardLLM
There are two common options for using LLM agents to edit files:
1. **Rewrite the entire file**: reliable, but very expensive (in time and tokens), and for small changes/big files it is incredibly wasteful and difficult to interpret where the change was made.
2. **Make a patch**: using a patch format such as [UDF](https://en.wikipedia.org/wiki/Diff#:~:text=The%20unified%20format%20(or%20unidiff,input%20to%20the%20patch%20program.) can make edits much faster and more clearly, but is highly error-prone as current generation of LLMs often make mistakes with line numbers, leading spaces, capitalization, etc.

**The Solution**: Instead of asking the agent to call a tool with the new contents, give the agent an "Editor" tool which drops into a sub-agent with appropriate context. The simulated editor shows the state of the editor in plaintext, takes individual keystrokes, and 

## Roadmap
1. Simulated Vim bindings directly (instead of re-creating functionality such as copy-paste, undo, etc.)

## Installation
