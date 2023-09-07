from typing import Callable, List
import pynvim
import openai
import os
import re

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
    

def render_text(filename, text, rowOneIdx, colOneIdx, history: List[str]):
    # insert the cursor, then add line numbers.
    lines = text.split('\n')
    cols = len(lines[rowOneIdx - 1])
    with_cursor = insert_cursor(text, rowOneIdx, colOneIdx)
    with_line_numbers = add_line_numbers(with_cursor)
    cmdHistory = '\n'.join(history)
    return f"History of commands you ran:\n{cmdHistory}\n\n\n```{filename}\n{with_line_numbers}\n```\nCol {colOneIdx} of {cols}; Line {rowOneIdx} of {len(lines)};\n"
    # Cursor is at {rowOneIdx}:


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


def vim_gpt(get_vim: Callable, filename: str, content: str, prompt: str, max_calls: int = 10, delay_seconds: int = 0):
  history = []
  
  with get_vim() as nvim:
    nvim.command('setlocal buftype=nofile')
    nvim.command('set number')
    nvim.current.buffer[:] = content.split('\n')
    for i in range(max_calls):
      buf = '\n'.join(nvim.current.buffer[:])
      (line, col) = nvim.current.window.cursor
      print(f'LLM calling render_text with line={line}, col={col}')
      rendered = render_text(filename, buf, line, col, history)
      print(f'Current state at iteration {i}:\n{rendered}')
      cmd = llm_get_keystrokes([
        {"role": "system", "content": prompt },
        {"role": "user", "content": rendered }
      ])
      print(f'LLM calling cmd: "{cmd}"')
      history.append(cmd)
      nvim.command(f'echom "{cmd}"')
      if cmd == 'wq':
        break
      else:
        # this gets the command to show up in the UI
        
        nvim.command(cmd)
        # Wait for a few seconds so you can capture the action (useful for screen recording)
        if delay_seconds > 0:
           import time
           time.sleep(delay_seconds)
    
    (line, col) = nvim.current.window.cursor
    final = render_text(filename, buf, line, col, history)
    print(f'LLM exited vim. Final state:\n{final}')
    return buf
    