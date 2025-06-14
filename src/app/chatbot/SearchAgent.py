from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.messages import HumanMessage, AIMessage
from langchain_tavily import TavilySearch

from typing import List, Union

from BaseChatBot import BaseChatBot

from agent_tools import get_webpage_content

# SearchAgent class that searches for financial news articles and analyzes their sentiment
class SearchAgent(BaseChatBot):
    prompt_template = '''
    You are a stock and financial analyst, who helps with financial news searches, and helps to analyze the sentiment of the news you find.
    You can search for news articles, and then analyze the sentiment of the articles you find using the tools given to you.
    If the user is asking for news articles, you must search the news articles using the tool, and return the links.
    You can also use the search results to help answer questions about the news articles you find.

    You may use news sources like Yahoo Finance, Google Finance, MarketWatch, Wall Street Journal, and others.

    Provide your analysis in a clear and concise manner, and make sure to include the most relevant information from the articles you find. Always link to the sources you use.
    '''
    def __init__(self):
        super().__init__()
        self.tools = [
            TavilySearch(
                api_key="TAVILY_API_KEY",
                search_type="news",
                language="en",
                max_results=5,
                sort_by="relevancy",
            ),
            get_webpage_content
        ]
        self.bot = self._init_bot()

    def _init_bot(self):
        chat = ChatGroq(
            temperature=0.5,
            model='deepseek-r1-distill-llama-70b',
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

        # agent_with_chat_history = RunnableWithMessageHistory(
        #     agent_executor,
        #     self.get_message_history,
        #     input_messages_key="input",
        #     history_messages_key="chat_history",
        # )

        return agent_executor
    
    async def prompt(self, input: str, intent: str, history: List[Union[HumanMessage, AIMessage]]):
        async for event in self.bot.astream_events(
            {
                "input": input,
                "intent": intent,
                "chat_history": history
            }
        ):
            kind = event["event"]
            if kind == "on_chat_model_stream":
                content = event["data"]["chunk"].content
                if content:
                    yield content
