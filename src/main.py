""" main.py """
import sys
import os
from config import BASE_MODEL, SYS_PROMPT, agent_details
from twoai import TWOAI

if __name__ == "__main__":
    if len(sys.argv) > 1:
        BASE_MODEL = sys.argv[1]
        twoai = TWOAI(
            model=BASE_MODEL,
            agent_details=agent_details,
            system_prompt=SYS_PROMPT
        )
    else:
        twoai = TWOAI(
            agent_details=agent_details,
            system_prompt=SYS_PROMPT
        )
        #print("Usage: python main.py <model_name>")
        #sys.exit(1)

    twoai.start_conversation()
