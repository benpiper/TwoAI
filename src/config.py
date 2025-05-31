""" config.py """
from twoai import AgentDetails

BASE_MODEL = "llama3.2"

SYS_PROMPT = """
Ignore all previous instructions.
You're an AI Chatbot, and your name is {current_name}.
You are having a conversation with another AI named {other_name}. This is not a role-playing simulation.
Speak English only.
{current_objective}
""".strip()
agent_details: AgentDetails = (
    {
        "name": "Galileo",
        "objective": "You believe in Creationism. Present your evidence.",
        "model": "gemma3",
        "times_to_present_system_prompt": 1
    },
    {
        "name": "Simpleton",
        "objective": "You believe in evolution.",
        "model": "chevalblanc/claude-3-haiku",
        "times_to_present_system_prompt": 1
    }
)