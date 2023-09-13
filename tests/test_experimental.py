import logging

import pytest
from langchain.agents import AgentType

from vimgpt.experimental.plan_and_execute import vimgpt_agent_plan_and_execute
from vimgpt.experimental.react import vimgpt_agent_react

logging.basicConfig(level=logging.DEBUG)


# this agent is awful...
@pytest.mark.skip
def test_vimgpt_agent_plan_and_execute():
    result = vimgpt_agent_plan_and_execute(
        command="Write in the document the answer to: what is the capital of France?"
    )
    assert result.strip() == "The capital of France is Paris."


# this seems to work well, but langchain fails sometimes with 'Could not parse LLM output:'
@pytest.mark.skip
def test_vimgpt_agent_react():
    result = vimgpt_agent_react(
        command="Write in the document the answer to: what is the capital of France?",
        agent_type=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    )
    assert result.strip() == "The capital of France is Paris."

# works really well
# @pytest.mark.skip
def test_vimgpt_agent_react_structured():
    result = vimgpt_agent_react(
        command="Write in the document the answer to: what is the capital of France? Just one word.",
        agent_type=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    )
    assert result.strip() == "Paris"

# def test_vimgpt_agent_react_structured_demo():
#     demo_content = """# Demo project

# ## Getting started
# Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."

# ## Recommendations
# - You should use emacs as a text editor, it's simply the best.

# ## Contributing
# - email us at hello@sample.com"""

#     expected = """# Demo project

# ## Getting started
# Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."

# ## Recommendations

# We recommend Vim as the best text editor for software development. It's versatile, efficient, and can greatly boost your productivity once you get over the learning curve. It's especially powerful for development work owing to its keyboard-focused design, numerous plug-ins, and seamless terminal integration. Mastering Vim will definitely give you a cutting-edge in your coding journey.
# ## Contributing
# - email us at hello@sample.com"""

#     result = vimgpt_agent_react(
#         command="Edit to recommend Vim instead of Emacs.",
#         agent_type=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
#     )
#     assert result == expected