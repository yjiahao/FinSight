from langchain_core.messages import HumanMessage, AIMessage
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_redis import RedisConfig, RedisVectorStore

import redis

import asyncio

from app.backend.core.config import settings

# NOTE: before this, run the following: docker run -d -p 6379:6379 -p 8001:8001 redis/redis-stack:latest

# chat history class that uses Redis as a vector store
class ChatHistory:
    def __init__(self, session_id: str):
        self.session_id = session_id

        # initalize Redis client
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        self.config = RedisConfig(
            index_name=self.session_id,
            redis_url=settings.redis_url,
            metadata_schema=[
                {
                    "name": "sender",
                    "type": "tag"
                }
            ]
        )
        # intialize embedding model
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
        # initialize Redis vector store as chat history
        self.chat_history = RedisVectorStore(
            config=self.config,
            embeddings=self.embeddings
        )

    def clear_history(self):
        """Clear the chat history for the session."""
        self.chat_history.clear()

    def retrieve(self, query: str, num_messages: int=5):
        """Retrieve the last `num_messages` messages from the chat history."""
        history_retriever = self.chat_history.as_retriever(search_type="similarity", search_kwargs={"k": num_messages}) # return 5 by default
        history = history_retriever.invoke(query)

        # to distinguish between human and AI messages, we added the metadata field 'sender'
        history = [
            HumanMessage(content=doc.page_content) if doc.metadata['sender'] == 'human' else AIMessage(content=doc.page_content) for doc in history
        ]

        return history
    
    async def add_messages(self, messages: list[str], metadata: list[dict[str, str]]):
        asyncio.create_task(self.chat_history.aadd_texts(messages, metadata))