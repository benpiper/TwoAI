""" twoai.py """
import datetime
import sys
import logging
from difflib import SequenceMatcher
from colorama import Fore, Style
from ollama import Client
from . import AgentDetails, Agent, DEFAULT_HOST

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("debug.log"),
              logging.StreamHandler(sys.stdout)],
)

logging.getLogger("httpx").setLevel(logging.WARNING)

class TWOAI:
    """
    Class representing an AI that can engage in a conversation with another AI.

        ai_details (AIDetails): Details of the AI including name and objective.
        model (str): The model used by the AI.
        system_prompt (str): The prompt for the AI conversation system.
        max_tokens (int): The maximum number of tokens to generate in the AI response.
        num_context (int): The number of previous messages to consider in the AI response.
        extra_stops (list): Additional stop words to include in the AI response.
        exit_word (str): The exit word to use in the AI response. Defaults to "<DONE!>".
        max_exit_words (int): The maximum number of exit words to include in the AI 
                              responses for the conversation to conclude. Defaults to 2.
    """

    def __init__(
        self,
        model: str,
        agent_details: AgentDetails,
        system_prompt: str,
        max_tokens: int = 4094,
        num_context: int = 4094,
        extra_stops: list[str] = [],
        exit_word: str = "<DONE!>",
        temperature: float = 0.8,
        max_exit_words: int = 2,
        similarity_ratio_warning_threshold: float = 0.4,
        similarity_ratio_exit_threshold: float = 0.8
    ) -> None:
        self.agent_details = agent_details
        self.model = model
        self.system_prompt = system_prompt
        self.max_tokens = max_tokens
        self.num_context = num_context
        self.extra_stops = extra_stops
        self.temperature = temperature

        self.messages = ""
        self.conversation = []
        self.current_agent = agent_details[0]

        self.exit_word = exit_word
        self.exit_word_count = 0
        self.max_exit_words = max_exit_words
        self.similarity_ratio_warning_threshold = similarity_ratio_warning_threshold
        self.similarity_ratio_exit_threshold = similarity_ratio_exit_threshold
        logging.debug("Model: %s", model)
        logging.debug(system_prompt)

    def bot_say(self, msg: str, color: str = Fore.LIGHTGREEN_EX):
        """ Print the agent's message """
        print(color + msg.strip() + "\t\t" + Style.RESET_ALL)

    def get_opposite_ai(self) -> Agent:
        """ Return the details of the opposite agent """
        if self.current_agent['name'] == self.agent_details[0]['name']:
            logging.debug("Opposite agent is %s", self.agent_details[1]['name'])
            return self.agent_details[1]
        logging.debug("Opposite agent is %s", self.agent_details[0]['name'])
        return self.agent_details[0]

    def get_updated_template_str(self):
        result = self.system_prompt.replace(
            "{current_name}", self.current_agent['name'])
        result = result.replace("{current_objective}",
                                self.current_agent['objective'])

        other_ai = self.get_opposite_ai()
        result = result.replace("{other_name}", other_ai["name"])
        result = result.replace("{other_objective}", other_ai["objective"])
        return result

    def __show_cursor(self):
        print("\033[?25h", end="")

    def __hide_cursor(self):
        print('\033[?25l', end="")

    def next_response(self, show_output: bool = False) -> str:
        """ Send prompt """
        if len(self.agent_details) < 2:
            raise ValueError("Not enough AI details provided")

        other_ai = self.get_opposite_ai()
        instructions = self.get_updated_template_str()
        convo = f"""
        {instructions}

        {self.messages}
        """

        current_model = self.model
        if model := self.current_agent.get('model', None):
            current_model = model

        current_host = DEFAULT_HOST
        if host := self.current_agent.get('host', None):
            current_host = host

        if show_output:
            self.__hide_cursor()
            print(
                Fore.YELLOW + f"{self.current_agent['name']} is thinking..." + Style.RESET_ALL, end='\r')

        logging.info("%s is thinking...", self.current_agent['name'])
        logging.debug("Current prompt: %s", convo.strip())
        ollama = Client(host=current_host)
        resp = ollama.generate(
            model=current_model,
            prompt=convo.strip(),
            stream=False,
            options={
                "num_predict": self.max_tokens,
                "temperature": self.temperature,
                "num_ctx": self.num_context,
                "stop": [
                    "<|im_start|>",
                    "<|im_end|>",
                    "###",
                    "\r\n",
                    "<|start_header_id|>",
                    "<|end_header_id|>",
                    "<|eot_id|>",
                    "<|reserved_special_token",
                    f"{other_ai['name']}: " if self.current_agent['name'] != other_ai['name'] else f"{self.current_agent['name']}: "

                ] + self.extra_stops
            }
        )

        text: str = resp['response'].strip()
        if not text:
            # print(Fore.RED + f"Error: {self.current_agent['name']} made an empty response,trying again." + Style.RESET_ALL)
            logging.warning(
                "%s made an empty response,trying again.", self.current_agent['name'])
            return self.next_response(show_output)

        if not text.startswith(self.current_agent['name'] + ": "):
            text = self.current_agent['name'] + ": " + text
        self.messages += text + "\n"

        if show_output:
            # print("\x1b[K",end="") # remove "thinking..." message
            if self.agent_details.index(self.current_agent) == 0:
                self.bot_say(text)
            else:
                self.bot_say(text, Fore.BLUE)

        self.current_agent = self.get_opposite_ai()
        self.__show_cursor()
        return text

    def start_conversation(self):
        """ Function to start the conversation """
        logging.info("=== Starting conversation ===")
        try:
            while True:
                res = self.next_response(show_output=False)
                self.conversation.append(res)
                logging.info(res)
                if len(self.conversation) > 1:
                    similarity_ratio = SequenceMatcher(
                        None, self.conversation[-1], self.conversation[-2]).ratio()
                    logging.info(
                        "Similarity of last two messages: %s", similarity_ratio)
                    similarity_ratio_all = SequenceMatcher(
                        None, self.conversation[-1], ' '.join(self.conversation[:-1])).ratio()
                    logging.info("Similarity of all messages: %s",
                                 similarity_ratio_all)
                    if similarity_ratio > self.similarity_ratio_warning_threshold:
                        logging.warning(
                            "Similarity ratio warning threshold exceeded. Agents may be stuck in a loop.")
                    if similarity_ratio > self.similarity_ratio_exit_threshold:
                        logging.warning(
                            "Similarity ratio exit threshold exceeded. Terminating conversation.")
                        return
                if self.exit_word in res:
                    self.exit_word_count += 1
                    logging.info("Exit word detected.")
                if self.exit_word_count == self.max_exit_words:
                    print(
                        Fore.RED + "The conversation was concluded..." + Style.RESET_ALL)
                    logging.info("The conversation was concluded...")
                    self.__show_cursor()
                    return
        except KeyboardInterrupt:
            print(Fore.RED + "Closing Conversation..." + Style.RESET_ALL)
            logging.info("Closing Conversation...")
            self.__show_cursor()
            return
