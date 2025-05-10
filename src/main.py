import sys
import os
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from twoai import TWOAI, AgentDetails

#BASE_MODEL = "llama3.2"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        BASE_MODEL = sys.argv[1]
    else:
        print("Usage: python main.py <model_name>")
        sys.exit(1)

    sys_prompt = """
You are a very intelligent AI Chatbot, and your name is {current_name}.
You will be having a conversation with another AI named {other_name}.
{current_objective} Repeat "<DONE!>" ONLY if you both established and agreed that you came to the end of the discussion. Do not repeat yourself.
""".strip()
    agent_details: AgentDetails = (
        {
            "name": "Galileo",
            "objective": "Debate the existence of God with your opponent. Use the argument from morality, the fine-tuning argument, and first cause argument."
        },
        {
            "name": "Fool",
            "objective": "Debate the existence of God. You are an atheist. Your opponent is a theist. Draw an inference to the best explanation."
        }
    )
    twoai = TWOAI(
        model=BASE_MODEL, 
        agent_details=agent_details, 
        system_prompt=sys_prompt,

    )
    twoai.start_conversation()