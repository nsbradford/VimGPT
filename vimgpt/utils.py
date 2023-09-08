import re
from typing import List, Optional, Tuple


def extract_cmd_content(s):
    pattern = r"<cmd>(.*?)</cmd>"
    match = re.search(pattern, s, re.DOTALL)  # re.DOTALL makes . match newlines as well
    return match.group(1) if match else None


def add_line_numbers(text):
    lines = text.split("\n")
    return "\n".join([f"{idx}:{line}" for idx, line in enumerate(lines, 1)])


def render_text(file_path: Optional[str], text: str, cursor: Tuple[int, int], history: List[str]):
    (rowOneIdx, colOneIdx) = cursor
    # insert the cursor, then add line numbers.
    lines = text.split("\n")
    cols = len(lines[rowOneIdx - 1])
    with_cursor = insert_cursor(text, rowOneIdx, colOneIdx)
    with_line_numbers = add_line_numbers(with_cursor)
    cmdHistory = "\n".join(history)
    prefix = f"History of commands you ran:\n{cmdHistory}\n\n\n"
    filename = file_path or ""
    filewrapped = f"```{filename}\n{with_line_numbers}\n```"
    postfix = f"\nCol {colOneIdx} of {cols}; Line {rowOneIdx} of {len(lines)};\n"
    return prefix + filewrapped + postfix


def insert_cursor(text, rowOneIdx, col):
    """
    Rows are one-indexed, columns are zero-indexed
    """
    row = rowOneIdx - 1
    # Split the text into rows
    rows = text.split("\n")

    # Ensure valid row and col
    if row < 0 or row >= len(rows):
        raise ValueError("Invalid row.")
    if col < 0 or col > len(rows[row]):
        raise ValueError("Invalid column.")

    # Calculate position to insert cursor; +1 accounts for newline characters
    pos = sum(len(r) + 1 for r in rows[:row]) + col + 1

    # Insert the combining low line character at the determined position
    return text[:pos] + "\u0332" + text[pos:]
