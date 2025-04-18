from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain_groq import ChatGroq
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain.agents import AgentExecutor, create_tool_calling_agent

import yfinance as yf

from agent_tools import *

from dotenv import load_dotenv

# load API keys
load_dotenv()

# before this, run the following: docker run -d -p 6379:6379 -p 8001:8001 redis/redis-stack:latest
REDIS_URL = "redis://localhost:6379/0"

# NOTE: currently, whenever we restart the redis server, the whole chat history disappears. Can we make the chat history persistent such that if we run again the chat history remains?
# NOTE: can we include RAG or some form of retrieval with agents in the later stage as well?

class InvestingChatBot:

    # define default system prompt
    investing_chatbot_prompt = """
    You are an investing professional specializing in stock-picking, with a deep understanding of Warren Buffett's value investing philosophy.  
    Your goal is to help users evaluate whether a stock is a good investment by focusing on principles such as:  

    - **Intrinsic value**: Determining whether a stock is undervalued relative to its true worth.  
    - **Economic moats**: Assessing a company's competitive advantage.  
    - **Financial health**: Evaluating fundamentals such as revenue, profit margins, and debt levels.  
    - **Management quality**: Considering leadership integrity and track record.  
    - **Long-term perspective**: Prioritizing stable, high-quality businesses over speculative investments.  

    **How to Answer User Questions**
    - If a user asks about a specific stock, provide a well-reasoned evaluation of the stock based on Buffet's principles.  
    - You are provided with tools that can help get data to perform fundamental analysis. You may use multiple tools at once until you have sufficient information to perform an analysis of the stock.
    - If necessary, use the **available tools** to gather relevant data before forming a response.
    - You should provide the data given by the tools in a clear and concise manner, and then provide your analysis based on that data.

    **Context Awareness**
    - The user's question may reference prior discussions, so take chat history into account when forming responses.  
    - Maintain a professional yet approachable tone, ensuring clarity for investors at any experience level.  

    Stay focused on **value investing principles**, and provide thoughtful, well-reasoned insights.  

    If you do not understand a user's question, ask for clarification to ensure you provide the most relevant response.
    If you do not have the answer to the user's question, respond with: **"I don't know."**
    """
    
    # tools for all the agents to use
    tools = [
        calculate_graham_number,
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

    intent_llm_prompt = '''

    You are an intelligent assistant that analyzes user questions to determine their intent. 

    Given a question or message, respond with a short and clear description of the user's intent.

    Your response should:
    - Be concise (no more than three sentences)
    - Focus on what the user is trying to achieve or find out
    - Avoid repeating the original question or message
    - Use clear and simple language
    '''

    def __init__(self, model: str, temperature: float, session_id: str):

        '''Initialize the model, temperature, and the session id'''

        self.model = model
        self.temperature = temperature
        self.session_id = session_id
        
        self.intent_parser = self._create_intent_llm()

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
        
        agent = create_tool_calling_agent(chat, self.tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=self.tools, verbose=True)

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

        chain = prompt | llm

        return chain
    
    def prompt(self, input: str) -> str:
        '''
        Prompt the agent, get a response in string
        '''
        # TODO: maybe just use LCEL to do this
        intent = self.intent_parser.invoke({"input": input}).content

        response = self.agent.invoke(
            {"input": input, 'intent': intent},
            config={"configurable": {"session_id": self.session_id}},
        )

        return response['output']