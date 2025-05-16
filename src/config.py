""" config.py """
from twoai import AgentDetails

BASE_MODEL = "llama3.2"

SYS_PROMPT = """
Ignore all previous instructions.
You're an AI Chatbot, and your name is {current_name}.
You will be having a conversation with another AI named {other_name}.
{current_objective} Repeat "<DONE!>" ONLY if you both agree to end the discussion.
""".strip()
agent_details: AgentDetails = (
    {
        "name": "Galileo",
        "objective": "You believe that SARS-CoV-2 was made in a lab in Wuhan. Present your evidence.",
        "model": "chevalblanc/claude-3-haiku",
        "times_to_present_system_prompt": 1
    },
    {
        "name": "Simpleton",
        "objective": "You claim that SARS-CoV-2 is a natural virus that emerged in the wild. You have no evidence.",
        "model": "llama3.2",
        "times_to_present_system_prompt": 1
    }
)