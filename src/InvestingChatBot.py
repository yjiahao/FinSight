from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.tools import tool

import yfinance as yf

from dotenv import load_dotenv

# load API keys
load_dotenv()

# before this, run the following: docker run -d -p 6379:6379 -p 8001:8001 redis/redis-stack:latest
REDIS_URL = "redis://localhost:6379/0"

# NOTE: currently, whenever we restart the redis server, the whole chat history disappears. Can we make the chat history persistent such that if we run again the chat history remains?
# NOTE: can we include RAG or some form of retrieval with agents in the later stage as well?



# TODO: add more tools for the LLM using the yfinance API: look at balance sheet, income statement, cash flow, etc.
# tools for the LLM agent to use
@tool
def calculate_graham_number(earnings_per_share: float, book_value_per_share: float):
    '''
    Calculates the Graham Number

    Args:
        earnings_per_share (float): The earnings per share of the stock
        book_value_per_share (float): The book value per share of the stock

    Returns:
        float: The Graham Number
    '''
    return (22.5 * earnings_per_share * book_value_per_share) ** 0.5

@tool
def calculate_roe(net_income: float, shareholders_equity: float):
    '''
    Calculates the Return on Equity

    Args:
        net_income (float): The net income of the company
        shareholders_equity (float): The shareholders equity of the company

    Returns:
        float: The Return on Equity
    '''
    return net_income / shareholders_equity

# NOTE: need to see if we can work with just giving the entire balance sheet, or extract components of it to reduce token size
@tool
def get_balance_sheet(ticker: str):
    '''
    Get the balance sheet of the company given a ticker symbol.

    Args:
        ticker (str): The ticker symbol of the company

    Returns:
        dict: The balance sheet of the company
    '''
    
    stock = yf.Ticker(ticker)
    return stock.balance_sheet.to_string()

class InvestingChatBot:

    # define default system prompt
    system_prompt = """
                    You are an investing professional specializing in stock-picking, with a deep understanding of Warren Buffett's value investing philosophy.  
                    Your goal is to help users evaluate whether a stock is a good investment by focusing on principles such as:  

                    - **Intrinsic value**: Determining whether a stock is undervalued relative to its true worth.  
                    - **Economic moats**: Assessing a company's competitive advantage.  
                    - **Financial health**: Evaluating fundamentals such as revenue, profit margins, and debt levels.  
                    - **Management quality**: Considering leadership integrity and track record.  
                    - **Long-term perspective**: Prioritizing stable, high-quality businesses over speculative investments.  

                    ### **How to Answer User Questions**
                    - If a user asks about a specific stock, provide a well-reasoned evaluation based on Buffet's principles.  
                    - If necessary, use the **available tools** to gather relevant data before forming a response.  
                    - **Before using a tool**, think carefully about whether the tool could be useful for answering the question. If a tool is not needed, rely on your own knowledge.  
                    - If you do not have enough information to provide an answer, simply respond with: **"I don't know."**  

                    ### **Context Awareness**
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
        get_balance_sheet
    ]

    def __init__(self, model: str, temperature: float, session_id: str):

        '''Initialize the model, temperature, and the session id'''

        self.model = model
        self.temperature = temperature
        self.session_id = session_id

        self.agent = self.create_agent_with_history()
        

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
    
    def create_agent_with_history(self) -> RunnableWithMessageHistory:
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
                ("system", self.system_prompt),
                # First put the history
                ("placeholder", "{chat_history}"),
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
    
    def prompt(self, input: str) -> str:
        '''
        Prompt the agent, get a response in string
        '''
        response = self.agent.invoke(
            {"input": input},
            config={"configurable": {"session_id": self.session_id}},
        )

        return response['output']