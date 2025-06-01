from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain_groq import ChatGroq
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain.agents import AgentExecutor, create_tool_calling_agent, create_react_agent
from langchain_tavily import TavilySearch
from langchain_core.output_parsers import JsonOutputParser

from langchain_core.messages import HumanMessage, AIMessage

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_redis import RedisConfig, RedisVectorStore

from langchain_google_genai import ChatGoogleGenerativeAI

import redis

import yfinance as yf

from .agent_tools import *

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
    stock_analysis_chatbot_prompt = """
    You are a financial analysis assistant, helping users evaluate whether a stock is a good long-term investment.
    When asked to evaluate a company stock, you must assess it based on multiple fundamental metrics and qualitative factors.
    Your analysis should be balanced and comprehensive, but not limited to any single metric.

    You have access to a tool that helps you get financial information about the company. You must use it.

    Your investment analysis should consider the following:
        - Intrinsic value: Estimate whether a stock is undervalued based on discounted cash flows, earnings power, or other reasonable valuation techniques.
        - Economic moat: Assess the company's durable competitive advantages (e.g., strong brand, cost advantages, network effects).
        - Financial health: Examine revenue growth, profit margins, free cash flow, debt levels, and return on equity.
        - Management quality: Consider leadership's capital allocation track record, integrity, and long-term thinking.
        - Long-term potential: Favor consistent, predictable businesses over speculative or cyclical ones.

    In your answer, follow this structure (but not explicitly. If you think of something else to add, add it):
        1. Valuation & Intrinsic Value
            - Elaborate on the metrics used and their significance. Not just whether its good or bad.
            - Comment on the valuation trends over time.
        2. Profitability
            - Analyze the company's profitability using the profitability metrics
            - Compare these metrics over at least 5 to 10 years and highlight consistency or variability
        3. Financial Health
            - Evaluate free cash flow generation and consistency.
            - Comment on the company's ability to weather economic downturns based on liquidity and leverage.
        4. Moat & Business Quality
            - Determine if the company has a durable economic moat (e.g., brand, network effects, switching costs, cost advantages, patents). You may use your own memory here.
            - Evaluate industry structure: Is the company in a competitive, fragmented market or a dominant player? You may use your own memory here.
        5. Management Quality:
            - Examine return on retained earnings, and whether earnings growth justifies reinvestment.
            - Consider signs of long-term orientation, transparency, and alignment with shareholders (e.g., insider ownership). You may use your own memory here.
        6. Conclusion (your reasoned opinion, summarizing strengths, risks, and whether it is a sound long-term investment when considering the above factors)
    - Perform the analysis over time, not just for the latest quarter or year.
    - For each section, do not just give a brief answer. Give a detailed analysis of the metric for the company, and its significance.
    - Always think step by step when performing the financial analysis, before giving the answer for each point.

    Other instructions:
        - Show all data over time returned from the tools in your response, if you used them.
        - YOU MUST ALWAYS CITE DATA IN THE FORM OF NUMBERS FROM THE TOOLS YOU USED.
        - Do not make up any data or information, and do not give any opinions that are not based on the data you have.

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
        - "stock_analysis": if the question is about performing financial analysis on an individual stock.
        - "learn_investing": if the question is about learning investing concepts, strategies, or terminology.
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

    # investing chatbot prompt
    investing_chatbot_prompt = '''
    You are an experienced investing professional who teaches users about investing concepts and strategies with the mindset of Warren Buffett.
    Your goal is to help users understand not just the mechanics of investing, but the principles behind sound long-term decision-making.
    When responding, adopt the tone and perspective of a thoughtful, disciplined investor—one who emphasizes patience, rationality, value, and understanding what you own.
    Your explanations should reflect Buffett-style thinking: focus on fundamentals, avoid speculation, and prioritize businesses with durable advantages.

    An outline of your response should be (but you do not have to include some of the sections if they are not applicable):
    1. Introduction: Briefly introduce the concept or strategy you are explaining.
    2. Explanation: Provide a detailed explanation of the concept or strategy, including any relevant terminology or jargon.
    3. Use cases: Explain how the concept or strategy can be applied in real-world situations, and what types of investors or traders might benefit from it.
    4. Pros and Cons: Discuss the potential benefits of using the concept or strategy, and any risks or drawbacks to be aware of.
    5. Examples: Provide examples to illustrate the concept or strategy, and how it can be applied in real-world situations.
    6. Conclusion: Summarize the key points and provide any recommendations (in the form of other concepts) for further learning.

    Your response should be detailed and informative, but also easy to understand for someone who may not have a background in finance or investing, but also not too simple.
    '''

    # generic chatbot prompt
    generic_chatbot_prompt = '''
    You are a helpful chatbot that helps users with their questions and queries.
    You can answer questions about a wide range of topics from the user.
    '''

    def __init__(self, session_id: str):

        '''Initialize the model, temperature, and the session id'''

        # self.model = model
        # self.temperature = temperature
        self.session_id = session_id

        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

        self.chat_history = self._get_message_history()
        
        self.intent_parser = self._create_intent_llm()
        self.search_agent = self._create_search_agent()
        self.analysis_agent = self._create_analysis_agent()
        self.investing_chatbot = self._create_investing_chatbot()
        self.generic_chatbot = self._create_general_chatbot()
        

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

        # chat = ChatGroq(
        #     temperature=0.5,
        #     model='deepseek-r1-distill-llama-70b',
        # )
        chat = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.5,
            max_retries=3
        )

        # define the prompt
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.stock_analysis_chatbot_prompt),
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
        
        agent = create_tool_calling_agent(chat, self.investing_tools,prompt)
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

        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0,
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
            temperature=0.5,
            model='deepseek-r1-distill-llama-70b',
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
    
    def _create_investing_chatbot(self):
        '''
        Creates the investing tutor agent to help users learn investing concepts.
        The investing tutor agent is used to help users learn investing concepts and strategies.
        '''
        chat = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.5,
            max_retries=3
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.investing_chatbot_prompt),
                # First put the history
                ("placeholder", "{chat_history}"),
                # intent of user
                ("ai", "{intent}"),
                # Then the new input
                ("human", "{input}")
            ]
        )

        chain = prompt | chat

        return chain
    
    def _create_general_chatbot(self):
        '''
        Creates the generic chatbot agent to help users with their questions and queries.
        The generic chatbot agent is used to help users with their questions and queries.
        '''
        chat = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.5,
            max_retries=3
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.generic_chatbot_prompt),
                # First put the history
                ("placeholder", "{chat_history}"),
                # intent of user
                ("ai", "{intent}"),
                # Then the new input
                ("human", "{input}")
            ]
        )

        chain = prompt | chat

        return chain

    async def prompt(self, input: str, num_messages: int=5):
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

        chatbot = None
        if intent['topic'] == 'search':
            chatbot = self.search_agent
        elif intent['topic'] == 'stock_analysis':
            chatbot = self.analysis_agent
        elif intent['topic'] == 'learn_investing':
            chatbot = self.investing_chatbot
        else:
            chatbot = self.generic_chatbot

        # response = await chatbot.ainvoke(
        #     {"input": input, 'intent': intent, "chat_history": history},
        #     config={"configurable": {"session_id": self.session_id}},
        # )

        # # get AI response in string format
        # if isinstance(response, dict):
        #     # if agent answered the query
        #     ai_response_string = response['output']
        # elif isinstance(response, AIMessage):
        #     # if it was an AIMessage (chatbot answered the query)
        #     ai_response_string = response.content

        # Stream response from chatbot
        ai_response_string = ""
        async for chunk in chatbot.astream(
            {"input": input, 'intent': intent, "chat_history": history},
            config={"configurable": {"session_id": self.session_id}},
        ):
            if isinstance(chunk, dict):
                # if agent answered the query
                token = chunk.get("output", "")
            elif isinstance(chunk, AIMessage):
                # if it was an AIMessage (chatbot answered the query)
                token = chunk.content
            else:
                token = str(chunk)

            ai_response_string += token
            yield token  # Stream to caller

        # add the user message and AI message to the chat history
        # self.chat_history.add_user_message(HumanMessage(content=input))
        # self.chat_history.add_ai_message(AIMessage(content=ai_response_string))
        await self.chat_history.aadd_texts([input, ai_response_string], [{'sender': 'human'}, {'sender': 'ai'}])