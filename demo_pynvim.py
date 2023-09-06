import pynvim
import openai
import os
import re


# Note: seems pretty bad with gpt-3.5, though XML parser works fine.

PROMPT_UPDATED = """You are VimGPT, an expert software developer  with the following goal:

<goal>
Edit the contents of the README file to recommend Vim as the best text editor.
</goal>

You interact with the world through structured Vim commands, which will be routed through the Python package pynvim and executed via `nvim.command(<your command>)`. You must respond in this format with the EACT text that should be given to `nvim.command()`. Remember, if you are using a normal mode command, you must prefix your command with 'normal'. Respond with ONLY <cmd> tag, do not provide any other comments or commentary.

<thoughts>CONCISE thoughts about what to do next</thoughts>
<cmd>The exact text that should be given to `nvim.command()`</cmd>

Examples:
- Enter insert mode: <cmd>normal i</cmd>
- Start search for "pattern": <cmd>/pattern</cmd>
- Delete a line: <cmd>normal dd</cmd>
- Move cursor to start of 11th line: <cmd>normal 7G</cmd>

When you are finished, close the session with "wq" command.
<cmd>wq</cmd>

Here is the file, which is already open in nvim:
"""


# PROMPT_ORIGINAL = """
# You are VimGPT, an expert software developer  with the following goal:

# <goal>
# Edit the contents of the README file to recommend Vim as the best text editor.
# </goal>

# You interact with the world through structured Vim commands, which will be routed through the Python package pynvim and executed via `nvim.command(<your command>)`. You must respond in this format:

# ```xml
# <thoughts>Some thoughts about what to do next</thoughts>
# <cmd>The exact text that should be given to `nvim.command()`</cmd>

# Examples
# - enter insert mode: 
# <cmd>normal i</cmd>


# When you are finished, close the session with ":wq" command, such as:

# <command>wq</command>

# Here is the file, which is already open in nvim:
# """


fileContents = """# Demo project

## Getting started
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."

## Recommendations
- You should use emacs as a text editor, it's simply the best.

## Contributing
- email us at hello@sample.com  
"""

def extract_cmd_content(s):
    pattern = r'<cmd>(.*?)</cmd>'
    match = re.search(pattern, s, re.DOTALL)  # re.DOTALL makes . match newlines as well
    return match.group(1) if match else None
    # Test
    # mixed_string = "... some content ... <cmd>YOUR_CONTENT_HERE</cmd> ... some other content ..."
    # print(extract_cmd_content(mixed_string))  # Outputs: YOUR_CONTENT_HERE

  
def add_line_numbers(text):
  lines = text.split('\n')
  return '\n'.join([f"{idx}:{line}" for idx, line in enumerate(lines, 1)])
    

def render_text(filename, text, rowOneIdx, colOneIdx):
    # insert the cursor, then add line numbers.
    with_cursor = insert_cursor(text, rowOneIdx, colOneIdx)
    with_line_numbers = add_line_numbers(with_cursor)
    return f"Cursor at {rowOneIdx}:{colOneIdx}\n```{filename}\n{with_line_numbers}\n```"


def insert_cursor(text, rowOneIdx, col):
    """
    Rows are one-indexed, columns are zero-indexed
    """
    row = rowOneIdx - 1
    # Split the text into rows
    rows = text.split('\n')
    
    # Ensure valid row and col
    if row < 0 or row >= len(rows):
        raise ValueError("Invalid row.")
    if col < 0 or col > len(rows[row]):
        raise ValueError("Invalid column.")
    
    # Calculate position to insert cursor
    pos = sum(len(r) + 1 for r in rows[:row]) + col + 1 # +1 accounts for newline characters
    
    # Insert the combining low line character at the determined position
    return text[:pos] + '\u0332' + text[pos:]
  

def llm_get_keystrokes(messages):
  # openai.api_base = "https://oai.hconeai.com/v1"
  chat_completion = openai.ChatCompletion.create(
    model='gpt-4',
    messages=messages,
    api_key=os.environ['OPENAI_API_KEY'],
    api_base="https://oai.hconeai.com/v1",
    headers={
      "Helicone-Auth": f"Bearer {os.environ['HELICONE_API_KEY']}",
      "Helicone-Cache-Enabled": "true",
    }
  )
  text = chat_completion.choices[0].message.content
  parsed = extract_cmd_content(text)
  return parsed

def vim_gpt(filename: str, content: str, prompt: str, max_calls: int = 3):
  with pynvim.attach('child', argv=["nvim", "--embed", "--headless"]) as nvim:
    nvim.current.buffer[:] = content.split('\n')
    for i in range(max_calls):
      buf = '\n'.join(nvim.current.buffer[:])
      (line, col) = nvim.current.window.cursor
      print(f'LLM calling render_text with line={line}, col={col}')
      rendered = render_text(filename, buf, line, col)
      print(f'Current state at iteration {i}:\n{rendered}')
      cmd = llm_get_keystrokes([
        {"role": "system", "content": prompt },
        {"role": "user", "content": rendered }
      ])
      print(f'LLM calling cmd: "{cmd}"')
      if cmd == 'wq':
        break
      else:
        nvim.command(cmd)
    
    (line, col) = nvim.current.window.cursor
    final = render_text(filename, buf, line, col)
    print(f'LLM exited vim. Final state:\n{final}')
    
if __name__ == '__main__':
  vim_gpt('README.md', fileContents, PROMPT_UPDATED)


## Scratch

# with pynvim.attach('child') as nvim:
#     # Insert some text
#     nvim.command('normal iHello, Vim from Python!')
    
#     # Get buffer content
#     buf = nvim.current.buffer
#     print(buf[:])  # ['Hello, Vim from Python!']

# "/bin/env", 
# with pynvim.attach('child', argv=["nvim", "--embed", "--headless"]) as nvim:
#     while True:
#       cursorRow = nvim.current.cursorRow
#       cursorCol = nvim.current.cursorCol
#       # nvim.command('set number')
#       # Insert some text
#       # nvim.command(f'normal i{fileContents}')
#       nvim.current.buffer[:] = fileContents.split('\n')
#       buf = nvim.current.buffer
#       rendered = render_text(filename, '\n'.join(buf[:]), cursorRow, cursorCol)
      
#       # Get buffer content
#       # buf = nvim.current.buffer
#       print(rendered)  # ['Hello, Vim from Python!']