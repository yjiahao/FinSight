from langchain_core.messages import HumanMessage, AIMessage
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_redis import RedisConfig, RedisVectorStore
from langchain_redis.chat_message_history import RedisChatMessageHistory

import redis

import asyncio

from app.backend.core.config import settings

# NOTE: before this, run the following: docker run -d -p 6379:6379 -p 8001:8001 redis/redis-stack:latest

# chat history class that uses Redis as a vector store
class ChatHistory:
    def __init__(self, session_id: str, embeddings: HuggingFaceEmbeddings):
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
        # initialize Redis vector store as chat history for LLM to retrieve messages from
        self.vector_store = RedisVectorStore(
            config=self.config,
            embeddings=embeddings
        )

        # initialize the chat message history for persistence and frontend display
        self.chat_message_history = RedisChatMessageHistory(
            session_id=self.session_id,
            redis_url=settings.redis_url,
            redis_client=self.redis_client
        )

    def clear_history(self):
        """Clear the chat history for the session."""
        # clear chat message history
        self.chat_message_history.clear()
        
        # clear vector store documents
        keys = self.redis_client.keys(f"{self.session_id}:*")
        if keys:
            self.redis_client.delete(*keys)

    def retrieve(self, query: str, num_messages: int=5):
        """Retrieve the last `num_messages` messages from the chat history."""
        history_retriever = self.vector_store.as_retriever(search_type="similarity", search_kwargs={"k": num_messages}) # return 5 by default
        history = history_retriever.invoke(query)

        # to distinguish between human and AI messages, we added the metadata field 'sender'
        history = [
            HumanMessage(content=doc.page_content) if doc.metadata['sender'] == 'human' else AIMessage(content=doc.page_content) for doc in history
        ]

        return history
    
    async def add_messages(self, messages: list[str], metadata: list[dict[str, str]]):

        # add to chat history for frontend display
        history_messages = [
            HumanMessage(content=message) if meta['sender'] == 'human' else AIMessage(content=message)
            for message, meta in zip(messages, metadata)
        ]
        asyncio.create_task(self.chat_message_history.aadd_messages(history_messages))
        
        # add to chat history vector store
        asyncio.create_task(self.vector_store.aadd_texts(messages, metadata))