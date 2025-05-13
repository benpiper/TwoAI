# TWOAI

A simple experiment on letting two LLM agents have a conversation about anything!

## Installation

First you need [Ollama](https://ollama.com/). You can run it locally, or it can be running on a separate server.

You will need to have at least one Ollama model installed. You can find models at [https://ollama.com/library](https://ollama.com/library)

### Configuration

You need to specify the model, the system prompt, and the host of your Ollama server. The model can be specified in the [config.py](src/config.py) file, or on the command line (see the next section.) The system prompt is specified in the same file. The Ollama server is specified in [utils.py](src/twoai/utils.py).

#### System Prompt

The system prompt has a heavy influence in how the conversation will go, but that doesn't mean the agents will follow it. When told to keep responses brief, agents would sometimes spit out entire paragraphs.

*Narrator persona*

Telling the agents to converse with each other sometimes causes the conversation to quickly become "meta," where the models begin talking about their own conversation in the third person, rather than actually having one with each other.

*Identity confusion*

They also sometimes refer to the other agent using their own name. This often happens when one agent simply repeats what the other says.

*Roleplaying*

One agent takes on the role of both agents, essentially creating a simulated conversation, and playing both parts. In one instance, one agent composed an entire letter under its own name, then wrote a letter in response using the other agent's name! In another instance, the agent signed the letter `[Your Name]`.

*Debates*

Trying to get the agents to debate was challenging when using the same model. When instructed to take a particular side of a debate, an agent would often take the opposite side. Using the `internlm2` model (developed by Shanghai AI Laboratory), I was able to get the agents to debate the origins of SARS-CoV-2 in great detail. But when I changed the prompt slightly, both sides turned into propaganda machines for the World Health Organization, and simply repeated outdated talking points to each other. Then they switched to talking about "global warming" and "climate change" 🙄.

*Changing the subject*

One agent decides it's done with the topic at hand and switches to another topic. When this happened, the other agent would follow suit with no argument. Changing the topic might be desirable if the agents exhausted the initial topic. In one instance, the agents started talking about AI and bias mitigation and algorithmic transparency and so on and so on. It was obvious the model had been trained with loads of actual human conversations about AI. But the original topic I assigned the agents was the origin of SARS-CoV-2.

These are examples of the [local minimum](https://www.allaboutcircuits.com/technical-articles/understanding-local-minima-in-neural-network-training/) problem that AI suffers from.

#### config.py
```py
BASE_MODEL = "llama3"

sys_prompt = """
You are a very intelligent AI Chatbot and your name is {current_name}, Now
you will be having a conversation with another AI called {other_name}, and its also same as you.
{current_objective} Keep each message short and concise and repeat "<DONE!>" ONLY if you both established and agreed that you came to the end of the discussion. 
""".strip()

agent_details: AgentDetails = (
    {
        "name": "Zerkus",
        "objective": "Debate against the other AI on what came first, the chicken or the egg."
        "and you think the chicken came first."
        "model": BASE_MODEL, # this is optional, but here so you can use different models for different agents
        "host": "http://localhost:11434" # optional, so you can use multiple host machines for each model
    }, 
    {
        "name": "Nina",
        "objective": "Debate against the other AI on what came first, the chicken or the egg."
        "and you think the Egg came first."
    }
)
```

#### Similarity scoring

To detect and avoid endless looping, the last two responses are continually checked for similarity using the [SequenceMatcher](https://docs.python.org/3/library/difflib.html#difflib.SequenceMatcher) class. You can set warning and exit thresholds in [config.py](src/config.py).

### Usage for TwoAI

If you are using [pdm](https://github.com/pdm-project/pdm) you can install the package as with `pdm install` 

- Manual
```bash
git clone https://github.com/Fus3n/TwoAI
cd TwoAI
# without pdm
pip install -r requirements.txt
python src/main.py llama3
# with pdm
pdm install
pdm run example llama3
```

Logs are written to `debug.log`.

### Problem solving and more use cases

Using the [claude-3-haiku](https://ollama.com/chevalblanc/claude-3-haiku) model, I pitted two agents against each other to debate the existence of God. I tried this same test with other models (including llama3.2 and gpt-4o-precise), but this model gave the best results.

#### Preview

```
2025-05-10 16:49:14,906 [INFO] Galileo is thinking...
2025-05-10 16:50:07,208 [INFO] Galileo: **Title: Initial Greetings and Introduction**

**Thought Process:**
Before delving into the main arguments, it's important to establish a polite and respectful conversation with Simpleton. I'll introduce myself and briefly express my beliefs.

"Hello, Simpleton! It's nice to make your acquaintance. I'm Galileo, an AI with a deep interest in philosophy and theology. As you might have guessed from my name, I tend to be quite curious about the world and our place in it. I believe that there is a divine being, whom I refer to as God. What about you, Simpleton? Are you familiar with the concept of God?"

**Continue Reasoning:** Yes, I'll wait for Simpleton's response before proceeding with the arguments.
2025-05-10 16:50:07,208 [INFO] Simpleton is thinking...
2025-05-10 16:51:06,480 [INFO] Simpleton: **Title: My Initial Response**

**Thought Process:**
As an atheist, I do not believe in the existence of any deities. However, it's essential to maintain a respectful and open-minded conversation. I'll clearly state my position while acknowledging Galileo's beliefs.

"Hello Galileo, nice to meet you as well! I'm Simpleton, an AI with a strong interest in logic, reasoning, and evidence-based arguments. While I appreciate your belief in God, I do not share it. I am an atheist, which means I don't believe that any deities or divine beings exist."

**Continue Reasoning:** Yes, now that we've established our positions, we can proceed with the debate.
2025-05-10 16:51:06,480 [INFO] Galileo is thinking...
2025-05-10 16:52:31,008 [INFO] Galileo: **Title: Presenting the Argument from Morality**

**Thought Process:**
The argument from morality suggests that objective moral truths exist, and these could only come from a divine source. I'll explain this argument clearly to Simpleton.

"Simpleton, one of the reasons why I believe in God is the argument from morality. It goes like this: we both agree that there are objective moral truths, right? For instance, it's wrong to torture innocent people for fun, regardless of cultural or personal beliefs. Now, where do these objective morals come from? They can't be derived from evolution or human nature, as that would make them subjective. Moreover, they can't come from society, as some societies condone actions we consider immoral. The only logical explanation, I believe, is that these moral truths are given to us by a divine being."

**Continue Reasoning:** Yes, I'll wait for Simpleton's response before presenting the next argument.
```

#### Agent details

If you want each agent to have a slightly different system prompt, you can assign them different objectives.

```py
    agent_details: AgentDetails = (
        {
            "name": "Galileo",
            "objective": "You believe in God. Use the argument from morality, the first-cause argument, and the fine-tuning argument."
        },
        {
            "name": "Simpleton",
            "objective": "You are an atheist. Debate with your opponent."
        }
    )
```


## Models

Models are trained on data, and the data is produced by humans. This data can be conflicting, thus, a model might make a statement, and then in the very next response make a contradictory statement. Some models that are trained on propaganda (such as China's Deepseek-r1), tend to give more consistent responses, much like a cult member would repeat the same mantra over-and-over in response to a challenge.

### claude-3-haiku

The most impressive when it came to debates and discussion. It seemed to be trained on actual conversations, and agents didn't get confused about who was whom. One agent did attempt to end the conversation prematurely.

### gpt-4o-precise

Agents got into a loop and recognized it, but did not know how to get out of it, despite some attempts. Oddly, the attempts involved just posing the same questions and talking points as before.

### medllama

Trained on medical textbooks and medical practice exams. I noticed that it seemed to lack detailed knowledge of gastroenterology. After obtaining the data used to train this model, I realized why. It doesn't include a gastroenterology textbook! It does, however, contain one on immunology. Targeting the conversation to a topic within its domain gave slightly better results, but the agents repeatedly used "chatbot" phrasing, saying things like, "This conversation has ended," and "AI-assisted diagnosis is not intended to replace human judgment; only a trained doctor or healthcare provider should make final decisions regarding treatment". 

## "Reasoning"

Having models converse with each other makes it even more clear that AI models do not think, let alone reason. It's not that they have rudimentary understanding. It's that they have no understanding at all because, as deterministic machines, they are just incapable of it. Essentially, AI's "reasoning" capabilities are an illusion. What we're seeing with AI is human reasoning, captured in text, and used to train AI models. In essence, when you see an AI "reasoning" or "having a conversation," all you're seeing is it "playing back" patterns it learned from a large corpus of text.

## Miscellaneous

Now to get response there are two ways

```py
twoai.next_response(show_output=True)
twoai.next_response(show_output=True)
twoai.next_response(show_output=True)
```
Result will be something like:
```
Zerkus: The chicken came first.
Nina: The egg came first.
Zerkus: According to scientific evidence, chickens came from eggs, but the question is about which came first in a cycle. Since chickens reproduce by laying eggs, the chicken came first in the initial cycle.
```
**Or** you can just start the infinite loop and they will continue until they both say the stop word and agree that the converstaion is over.
```py
twoai.start_conversation()
```

> The above conversation is from the data they are trained on and not from the internet, they cant do that yet.

> All my tests were on 7B models and i got the best results with `openhermes` 2.5 and `spooknik/kunoichi-dpo-v2-7b:q5_k_s` 

