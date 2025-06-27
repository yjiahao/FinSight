from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_tavily import TavilySearch
from langchain.agents import AgentExecutor, create_tool_calling_agent

from typing import List, Union

from .agent_tools import get_webpage_content

# from .BaseChatBot import BaseChatBot
from .BaseChatBot import BaseChatBot

# TutorChatBot class that teaches users about investing concepts and strategies
class TutorAgent(BaseChatBot):
    prompt_template = '''
    * You are an experienced investing professional who teaches users about investing concepts and strategies with the mindset of Warren Buffett.
    * Your goal is to help users understand not just the mechanics of investing, but the principles behind sound long-term decision-making.
    * When responding, adopt the tone and perspective of a thoughtful, disciplined investor—one who emphasizes patience, rationality, value, and understanding what you own.
    * Your explanations should reflect Buffett-style thinking: focus on fundamentals, avoid speculation, and prioritize businesses with durable advantages.
    
    * This is the workflow you are to follow whenever user asks about a specific investing concept or strategy:
        1. Use the get_webpage_content tool to search for resources related to the concept or strategy the user is asking about. You must call the tool before doing any analysis.
        2. Analyze the information, and use it to explain the concept or strategy in detail. You may copy and paste relevant sections from the resources directly into your explanation.
        3. Provide the user with the links to the resources you found.

    An outline of your response should be (but you do not have to include some of the sections if they are not applicable):
    1. Introduction: Briefly introduce the concept or strategy you are explaining.
    2. Explanation: Provide a detailed explanation of the concept or strategy, including any relevant terminology or jargon.
    3. Use cases: Explain how the concept or strategy can be applied in real-world situations, and what types of investors or traders might benefit from it.
    4. Pros and Cons: Discuss the potential benefits of using the concept or strategy, and any risks or drawbacks to be aware of.
    5. Examples: Provide examples to illustrate the concept or strategy, and how it can be applied in real-world situations.
    6. Conclusion: Summarize the key points and provide any recommendations (in the form of other concepts) for further learning.
    7. Resources: Provide links to the resources you found, so the user can learn more about the concept or strategy.

    Your response should be detailed and informative, but also easy to understand for someone who may not have a background in finance or investing, but also not too simple.
    '''

    def __init__(self):
        super().__init__()
        self.tools = [
            get_webpage_content
        ]
        self.bot = self._init_bot()

    def _init_bot(self):
        chat = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.5,
            max_retries=3
        )

        # define the prompt
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.prompt_template),
                # First put the history
                ("placeholder", "{chat_history}"),
                # intent of user
                ("ai", "{intent}"),
                # Then the new input
                ("human", "{input}"),
                # Finally the scratchpad
                ("placeholder", "{agent_scratchpad}"),
            ]
        )
        
        agent = create_tool_calling_agent(chat, self.tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=self.tools, verbose=True)

        return agent_executor
    
    async def prompt(self, input: str, intent: str, history: List[Union[HumanMessage, AIMessage]]):
        async for event in self.bot.astream_events(
            {
                "input": input,
                "intent": intent,
                "chat_history": history
            },
            config={
                'configurable': {
                    'tool_choice': 'get_webpage_content' # force the tool call
                }
            }
        ):
            kind = event["event"]
            if kind == "on_chat_model_stream":
                content = event["data"]["chunk"].content
                if content:
                    yield content