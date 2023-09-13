from vimgpt.core import vimgpt_agent


def test_vimgpt_agent_basic():
    result = vimgpt_agent(
        model="gpt-4", command="Answer: what is the capital of France?"
    )
    assert result.strip() == "The capital of France is Paris."


def test_vimgpt_agent_demo():
    demo_content = """# Demo project

## Getting started
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."

## Recommendations
- You should use emacs as a text editor, it's simply the best.

## Contributing
- email us at hello@sample.com"""

    expected = """# Demo project

## Getting started
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."

## Recommendations

- You should use Vim as a text editor, it's simply the best.
## Contributing
- email us at hello@sample.com"""

    result = vimgpt_agent(
        model="gpt-4",
        command="Edit the contents of the README file to recommend Vim as the best text editor. Do nothing else, do not elaborate, just change the recommendation.",
        content=demo_content,
        file_path="README.md",
    )
    assert result == expected
