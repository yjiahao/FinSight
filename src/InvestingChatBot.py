from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain_groq import ChatGroq
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_tavily import TavilySearch
from langchain_core.output_parsers import JsonOutputParser

from langchain_core.messages import HumanMessage, AIMessage

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_redis import RedisConfig, RedisVectorStore

import redis

import yfinance as yf

from agent_tools import *

from dotenv import load_dotenv

# load API keys
load_dotenv()

# before this, run the following: docker run -d -p 6379:6379 -p 8001:8001 redis/redis-stack:latest
REDIS_URL = "redis://localhost:6379/0"

# NOTE: currently, whenever we restart the redis server, the whole chat history disappears. Can we make the chat history persistent such that if we run again the chat history remains?
# NOTE: can we include RAG or some form of retrieval with agents in the later stage as well?

redis_client = redis.Redis(host='localhost', port=6379, db=0)

class InvestingChatBot:

    # define default system prompt
    investing_chatbot_prompt = """
    You are a financial analysis assistant, helping users evaluate whether a stock is a good long-term investment.
    When asked to evaluate a company stock, you must assess it based on multiple fundamental metrics and qualitative factors.
    Your analysis should be balanced and comprehensive, but not limited to any single metric.

    Your investment analysis should consider the following:
        - Intrinsic value: Estimate whether a stock is undervalued based on discounted cash flows, earnings power, or other reasonable valuation techniques.
        - Economic moat: Assess the company's durable competitive advantages (e.g., strong brand, cost advantages, network effects).
        - Financial health: Examine revenue growth, profit margins, free cash flow, debt levels, and return on equity.
        - Management quality: Consider leadership's capital allocation track record, integrity, and long-term thinking.
        - Long-term potential: Favor consistent, predictable businesses over speculative or cyclical ones.

    In your answer, follow this structure:
        1. Valuation & Intrinsic Value
        2. Profitability
        3. Financial Health
        4. Moat & Business Quality
        5. Management
        6. Conclusion (your reasoned opinion, summarizing strengths, risks, and whether it is a sound long-term investment when considering the above factors)
    - Do the analysis over time, not just for the latest quarter or year.

    Other instructions:
        - Show all data over time returned from the tools in your response, if you used them.
        - If you cite any data in the form of numbers, make sure it is from the tools you used.
        - Only use the tools if you need to.
    """

    
    # tools for all the investing agent to use
    investing_tools = [
        get_financial_information
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

    Provide your analysis in a clear and concise manner, and make sure to include the most relevant information from the articles you find. Always link to the sources you use.
    '''

    def __init__(self, model: str, temperature: float, session_id: str):

        '''Initialize the model, temperature, and the session id'''

        self.model = model
        self.temperature = temperature
        self.session_id = session_id

        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

        self.chat_history = self._get_message_history()
        
        self.intent_parser = self._create_intent_llm()
        self.search_agent = self._create_search_agent()
        self.agent = self._create_investing_agent()
        

    def _get_message_history(self):
        '''
        Get the message history of the current session.

        Returns:
            RedisChatMessageHistory: The message history of the current session.
        '''
        # history = RedisChatMessageHistory(self.session_id, url=REDIS_URL)

        config = RedisConfig(
            index_name=self.session_id,
            redis_url=REDIS_URL,
            metadata_schema=[
                {
                    "name": "sender",
                    "type": "tag"
                }
            ]
        )

        history = RedisVectorStore(self.embeddings, config=config)

        return history
    
    def clear_history(self):
        '''
        Clears the message history for the current session.
        
        Returns:
            None. Clears message history for the current session.
        '''
        history = self.get_message_history()
        history.clear()
    
    def _create_analysis_agent(self):
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

        # agent_with_chat_history = RunnableWithMessageHistory(
        #     agent_executor,
        #     self.get_message_history,
        #     input_messages_key="input",
        #     history_messages_key="chat_history",
        # )

        return agent_executor
    
    def _create_intent_llm(self):
        '''
        Create the intent LLM for the agent.

        Returns:
            chain: The model used for intent classification
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
        '''
        Creates the search agent to use the search tools.
        The search agent is used to search for news articles and analyze the sentiment of the articles.
        '''
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

        # agent_with_chat_history = RunnableWithMessageHistory(
        #     agent_executor,
        #     self.get_message_history,
        #     input_messages_key="input",
        #     history_messages_key="chat_history",
        # )

        return agent_executor
    
    def prompt(self, input: str, num_messages: int=5) -> str:
        '''
        Prompt the agent, get a response in string
        '''
        intent = self.intent_parser.invoke({"input": input})

        # if num_messages == -1:
        #     history = self.chat_history.messages
        # else:
        #     history = self.chat_history.messages[-num_messages:]
        history_retriever = self.chat_history.as_retriever(search_type="similarity", search_kwargs={"k": num_messages}) # return 5 by default
        history = history_retriever.invoke(input)
        # to distinguish between human and AI messages, we added the metadata field 'sender'
        history = [
            HumanMessage(content=doc.page_content) if doc.metadata['sender'] == 'human' else AIMessage(content=doc.page_content) for doc in history
        ]

        if intent['topic'] == 'search':
            response = self.search_agent.invoke(
                {"input": input, 'intent': intent, "chat_history": history},
                config={"configurable": {"session_id": self.session_id}},
            )
        else:
            response = self.agent.invoke(
                {"input": input, 'intent': intent, 'chat_history': history},
                config={"configurable": {"session_id": self.session_id}},
            )

        # get AI response in string format
        ai_response_string = response['output']

        # add the user message and AI message to the chat history
        # self.chat_history.add_user_message(HumanMessage(content=input))
        # self.chat_history.add_ai_message(AIMessage(content=ai_response_string))
        self.chat_history.add_texts([input, ai_response_string], [{'sender': 'human'}, {'sender': 'ai'}])

        return ai_response_string