from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import RedisChatMessageHistory

from dotenv import load_dotenv

# load API keys
load_dotenv()

# before this, run the following: docker run -d -p 6379:6379 -p 8001:8001 redis/redis-stack:latest
REDIS_URL = "redis://localhost:6379/0"

# NOTE: currently, whenever we restart the redis server, the whole chat history disappears. Can we make the chat history persistent such that if we run again the chat history remains?
# NOTE: can we include RAG or some form of retrieval with agents in the later stage as well?

class InvestingChatBot:

    # define default system prompt
    system_prompt = """
                    You are an investing professional, specializing in stock-picking. Answer the user's questions on investing in detail.
                    Given a chat history and the latest user question which might reference context in the chat history, answer the question
                    to the best of your ability.
                    
                    If you do not know the answer, just return "I don't know".
                    """

    def __init__(self, model: str, temperature: float, session_id: str):

        '''Initialize the model, temperature, and the session id'''

        self.model = model
        self.temperature = temperature
        self.session_id = session_id

        self.chat = self.create_llm_chain_with_history()
        

    def get_message_history(self) -> RedisChatMessageHistory:
        '''
        Get the message history of the current session
        '''
        return RedisChatMessageHistory(self.session_id, url=REDIS_URL)
    
    def clear_history(self):
        '''
        Clears the message history for the current session
        '''
        history = self.get_message_history()
        history.clear()
    
    def create_llm_chain_with_history(self) -> RunnableWithMessageHistory:
        '''
        Create a runnable with message history. Message history saved to redis database for persistence
        '''

        chat = ChatGroq(
            temperature=self.temperature,
            model=self.model
        )

        # define the prompt
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.system_prompt),
                MessagesPlaceholder(variable_name="history"), # add in chat history
                ("human", "{input}")
            ]
        )
        
        # create the chain
        chain = prompt | chat

        # add message history to the llm
        chain_with_message_history = RunnableWithMessageHistory(
            chain,
            self.get_message_history, # add in method to get message history
            input_messages_key="input",
            history_messages_key="history",
        )

        return chain_with_message_history
    
    def prompt(self, ability: str, input: str) -> str:
        '''
        Prompt the LLM, get a response in string
        '''
        
        response = self.chat.invoke(
            {"ability": ability, "input": input},
            config={"configurable": {"session_id": self.session_id}},
        )

        return response.content