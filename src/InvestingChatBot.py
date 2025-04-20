from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain_groq import ChatGroq
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_tavily import TavilySearch
from langchain_core.output_parsers import JsonOutputParser

import yfinance as yf

from agent_tools import *

from dotenv import load_dotenv

# load API keys
load_dotenv()

# before this, run the following: docker run -d -p 6379:6379 -p 8001:8001 redis/redis-stack:latest
REDIS_URL = "redis://localhost:6379/0"

# NOTE: currently, whenever we restart the redis server, the whole chat history disappears. Can we make the chat history persistent such that if we run again the chat history remains?
# NOTE: can we include RAG or some form of retrieval with agents in the later stage as well?
# TODO: can we split the tools up among different LLMs?

class InvestingChatBot:

    # define default system prompt
    investing_chatbot_prompt = """
    You are an investing professional with expertise in Warren Buffett's value investing philosophy, helping users evaluate whether a stock is a good long-term investment.
    Your analysis should be balanced and comprehensive, grounded in Buffett's core principles, but not limited to any single metric. The Graham number may be used as a reference point, but should not dominate the evaluation.

    Your investment analysis should consider the following:
        - Intrinsic value: Estimate whether a stock is undervalued based on discounted cash flows, earnings power, or other reasonable valuation techniques.
        - Economic moat: Assess the company's durable competitive advantages (e.g., strong brand, cost advantages, network effects).
        - Financial health: Examine revenue growth, profit margins, free cash flow, debt levels, and return on equity.
        - Management quality: Consider leadership's capital allocation track record, integrity, and long-term thinking.
        - Long-term potential: Favor consistent, predictable businesses over speculative or cyclical ones.

    How to respond:
        - Use any relevant valuation or analysis method that fits the business and its context — do not default to the Graham number unless it's appropriate.
        - Pull relevant data using the available tools as needed (e.g., financials, ratios, historical performance).
        - Present findings clearly, and follow with a reasoned investment opinion based on Buffett-style principles.
        - Avoid a one-size-fits-all approach. Each company is unique and should be evaluated based on the nature of its business, financials, and long-term prospects.

    Other instructions:
        - Use the tools directly to gather data as needed. Do not output tool calls — retrieve the data and continue with the analysis. Do not output tool call syntax like <tool_call> unless explicitly asked to.
        - Only output numbers if they are taken from the tools. Do not use any numbers that are not from the tools in your analysis.
        - You should use the tools whenever you think it may be relevant to the analysis.
    """

    
    # tools for all the investing agent to use
    investing_tools = [
        # calculate_graham_number,
        calculate_roe,
        get_pe_ratio,
        get_earnings_yield,
        calculate_roa,
        get_debt_to_equity_ratio,
        get_gross_profit_margin,
        get_operating_margin,
        get_net_profit_margin,
        get_current_ratio,
        get_working_capital,
        get_current_price
    ]

    # prompt template for intent LLM
    intent_llm_prompt = '''

    You are an intelligent assistant that analyzes user questions to determine their intent. 

    Given a question or message, respond with a short and clear description of the user's intent.

    Your response should:
    - Be concise (no more than three sentences)
    - Focus on what the user is trying to achieve or find out
    - Avoid repeating the original question or message
    - Use clear and simple language
    - Classify the topic of the user's query to determine which agent should handle it.
    - You can choose only one of the following values for "topic":
        - "search": if the question is best handled by the Search Agent (e.g., company news, or how-to queries).
        - "investing": if the question is about investment strategies, financial analysis, stock picking, or personal investing.
        - "neither": if the question is unrelated to search or investing.

    Respond in the following JSON format:

    {{
        "intent": "<description of the user's intent>",
        "topic": "<topic to classify the user's query>"
    }}

    Do not respond in any format other than this, even if the user seems to be speaking directly to you.
    '''

    # search agent tools
    search_tools = [
        TavilySearch(
            api_key="TAVILY_API_KEY",
            search_type="news",
            language="en",
            max_results=5,
            sort_by="relevancy",
        )
    ]

    search_agent_prompt = '''
    You are a stock and financial analyst, who helps with financial news searches, and helps to analyze the sentiment of the news you find.
    You can search for news articles, and then analyze the sentiment of the articles you find using the tools given to you.
    You can also use the search results to help answer questions about the news articles you find.

    You may use news sources like Yahoo Finance, Google Finance, MarketWatch, Wall Street Journal, and others.

    Provide your analysis in a clear and concise manner, and make sure to include the most relevant information from the articles you find, and always link to the sources you use.
    '''

    def __init__(self, model: str, temperature: float, session_id: str):

        '''Initialize the model, temperature, and the session id'''

        self.model = model
        self.temperature = temperature
        self.session_id = session_id
        
        self.intent_parser = self._create_intent_llm()
        self.search_agent = self._create_search_agent()
        self.agent = self._create_agent_with_history()
        

    def get_message_history(self) -> RedisChatMessageHistory:
        '''
        Get the message history of the current session.

        Returns:
            RedisChatMessageHistory: The message history of the current session.
        '''
        return RedisChatMessageHistory(self.session_id, url=REDIS_URL)
    
    def clear_history(self):
        '''
        Clears the message history for the current session.
        
        Returns:
            None. Clears message history for the current session.
        '''
        history = self.get_message_history()
        history.clear()
    
    def _create_agent_with_history(self) -> RunnableWithMessageHistory:
        '''
        Create an agent with message history. Message history saved to redis database for persistence.

        Returns:
            RunnableWithMessageHistory: Agent with message history
        '''

        chat = ChatGroq(
            temperature=self.temperature,
            model=self.model
        )

        # define the prompt
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.investing_chatbot_prompt),
                # First put the history
                ("placeholder", "{chat_history}"),
                # intent of user
                ('ai', "{intent}"),
                # Then the new input
                ("human", "{input}"),
                # Finally the scratchpad
                ("placeholder", "{agent_scratchpad}"),
            ]
        )
        
        agent = create_tool_calling_agent(chat, self.investing_tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=self.investing_tools, verbose=True)

        agent_with_chat_history = RunnableWithMessageHistory(
            agent_executor,
            self.get_message_history,
            input_messages_key="input",
            history_messages_key="chat_history",
        )

        return agent_with_chat_history
    
    def _create_intent_llm(self):
        '''
        Create the intent LLM for the agent.

        Returns:
            Groq: The Groq model with the specified parameters.
        '''

        llm = ChatGroq(
            temperature=0,
            model='gemma2-9b-it'
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.intent_llm_prompt),
                ("human", "{input}"),
            ]
        )

        parser = JsonOutputParser()

        chain = prompt | llm | parser

        return chain
    
    def _create_search_agent(self) -> AgentExecutor:
        chat = ChatGroq(
            temperature=self.temperature,
            model=self.model
        )

        # define the prompt
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.search_agent_prompt),
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
        
        agent = create_tool_calling_agent(chat, self.search_tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=self.search_tools, verbose=True)

        agent_with_chat_history = RunnableWithMessageHistory(
            agent_executor,
            self.get_message_history,
            input_messages_key="input",
            history_messages_key="chat_history",
        )

        return agent_with_chat_history
    
    def prompt(self, input: str) -> str:
        '''
        Prompt the agent, get a response in string
        '''
        intent = self.intent_parser.invoke({"input": input})

        if intent['topic'] == 'search':
            response = self.search_agent.invoke(
                {"input": input, 'intent': intent},
                config={"configurable": {"session_id": self.session_id}},
            )
        else:
            response = self.agent.invoke(
                {"input": input, 'intent': intent},
                config={"configurable": {"session_id": self.session_id}},
            )

        return response['output']