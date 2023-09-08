from vimgpt.core import vimgpt_agent


def test_vimgpt_agent_basic():
    result = vimgpt_agent(command="Answer: what is the capital of France?")
    assert result == "The capital of France is Paris."
