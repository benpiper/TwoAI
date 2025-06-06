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

# logging.getLogger("httpx").setLevel(logging.WARNING)


class AIConfig:
    """
    Class representing the configuration of an AI.

    Attributes:
        model (str): The model used by the AI.
        max_tokens (int): The maximum number of tokens to generate in the AI response.
        num_context (int): The number of previous messages to consider in the AI response.
        extra_stops (list): Additional stop words to include in the AI response.
        temperature (float): The temperature of the AI response.
    """

    def __init__(
        self,
        model: str = None,
        max_tokens: int = 4094,
        num_context: int = 4094,
        extra_stops: list[str] = None,
        temperature: float = 0.8
    ) -> None:
        self.model = model
        self.max_tokens = max_tokens
        self.num_context = num_context
        if extra_stops is None:
            extra_stops = []
        self.extra_stops = extra_stops
        self.temperature = temperature


class ConversationConfig:
    """
    Class representing the configuration of a conversation.

    Attributes:
        system_prompt (str): The prompt for the AI conversation system.
        exit_word (str): The exit word to use in the AI response.
        max_exit_words (int): The maximum number of exit words to include in the AI
                              responses for the conversation to conclude.
        similarity_ratio_warning_threshold (float): The similarity ratio warning threshold.
        similarity_ratio_exit_threshold (float): The similarity ratio exit threshold.
    """

    def __init__(
        self,
        system_prompt: str,
        exit_word: str = "<DONE!>",
        max_exit_words: int = 2,
        similarity_ratio_warning_threshold: float = 0.3,
        similarity_ratio_exit_threshold: float = 0.6
    ) -> None:
        self.system_prompt = system_prompt
        self.exit_word = exit_word
        self.max_exit_words = max_exit_words
        self.similarity_ratio_warning_threshold = similarity_ratio_warning_threshold
        self.similarity_ratio_exit_threshold = similarity_ratio_exit_threshold


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
        agent_details: AgentDetails,
        system_prompt: str,
        model: str = "",
        exit_word_count: int = 0
    ) -> None:
        self.ai_config = AIConfig(model)
        self.conversation_config = ConversationConfig(system_prompt)
        self.agent_details = agent_details
        self.messages = ""
        self.conversation = []
        self.exit_word_count = exit_word_count
        # Start with the first agent in the agent_details config
        self.current_agent = agent_details[0]
        self.message_count = 0
        logging.debug(self.conversation_config.system_prompt)

    def bot_say(self, msg: str, color: str = Fore.LIGHTGREEN_EX):
        """ Print the agent's message """
        print(color + msg.strip() + "\t\t" + Style.RESET_ALL)

    def get_opposite_ai(self) -> Agent:
        """ Return the details of the opposite agent """
        if self.current_agent['name'] == self.agent_details[0]['name']:
            return self.agent_details[1]
        return self.agent_details[0]

    def get_updated_template_str(self):
        result = self.conversation_config.system_prompt.replace(
            "{current_name}", self.current_agent['name'])
        result = result.replace("{current_objective}",
                                self.current_agent['objective'])
        logging.debug("Current agent is %s", self.current_agent['name'])
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
        if self.current_agent['times_to_present_system_prompt'] > 0:
            prompt = f"""
            {instructions}

            {self.messages}
            """
        else:
            prompt = f"""
            {self.messages}
            """
        logging.debug("Times left to present prompt: %s",
                      self.current_agent['times_to_present_system_prompt'])
        if self.current_agent['times_to_present_system_prompt'] > 0:
            self.current_agent['times_to_present_system_prompt'] = self.current_agent['times_to_present_system_prompt'] - 1
        current_model = self.ai_config.model
        if model := self.current_agent.get('model', None):
            current_model = model
            logging.debug("Current agent model: %s", current_model)
        current_host = DEFAULT_HOST
        if host := self.current_agent.get('host', None):
            current_host = host

        if show_output:
            self.__hide_cursor()
            print(
                Fore.YELLOW + f"{self.current_agent['name']} is thinking..." + Style.RESET_ALL, end='\r')

        logging.info("%s is thinking...", self.current_agent['name'])
        logging.debug("Current prompt: %s", prompt.strip())
        ollama = Client(host=current_host)
        resp = ollama.generate(
            model=current_model,
            prompt=prompt.strip(),
            stream=False,
            options={
                "num_predict": self.ai_config.max_tokens,
                "temperature": self.ai_config.temperature,
                "num_ctx": self.ai_config.num_context,
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

                ] + self.ai_config.extra_stops
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
        self.message_count += 1
        return text

    def start_conversation(self):
        """ Function to start the conversation """
        logging.info("======= Starting conversation =======")
        try:
            while True:
                res = self.next_response(show_output=False)
                self.conversation.append(res)
                logging.info(res)
                if len(self.conversation) > 1:
                    similarity_ratio = SequenceMatcher(
                        None, self.conversation[-1], self.conversation[-2]).ratio()
                    logging.info(
                        "Similarity of last two messages: %s", round(similarity_ratio, 2))
                    similarity_ratio_all = SequenceMatcher(
                        None, self.conversation[-1], ' '.join(self.conversation[:-1])).ratio()
                    logging.info("Similarity of all messages: %s",
                                 round(similarity_ratio_all, 2))
                    if similarity_ratio > self.conversation_config.similarity_ratio_warning_threshold:
                        logging.warning(
                            "Similarity ratio warning threshold exceeded. Agents may be stuck in a loop.")
                    if similarity_ratio > self.conversation_config.similarity_ratio_exit_threshold:
                        logging.warning(
                            "Similarity ratio exit threshold exceeded. Terminating conversation.")
                        logging.info("Number of messages: %s",
                                     self.message_count)
                        return
                if self.conversation_config.exit_word in res:
                    self.exit_word_count += 1
                    logging.info("Exit word detected.")
                if self.exit_word_count == self.conversation_config.max_exit_words:
                    self.end_conversation()
                    return
        except KeyboardInterrupt:
            print(Fore.RED + "Closing Conversation..." + Style.RESET_ALL)
            logging.info("======= Closing Conversation =======")
            logging.info("Number of messages: %s", self.message_count)
            self.__show_cursor()
            return

    def end_conversation(self):
        """ Function to gracefully end the conversation """
        print(
            Fore.RED + "The conversation was concluded..." + Style.RESET_ALL)
        logging.info("======= Conversation Concluded =======")
        logging.info("Number of messages: %s", self.message_count)
        self.__show_cursor()
        return
