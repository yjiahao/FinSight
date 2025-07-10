import time

from langchain_huggingface import HuggingFaceEmbeddings

from typing import Dict, Tuple

from app.backend.chatbot.InvestingChatBot import InvestingChatBot
from app.backend.chatbot.ChatHistory import ChatHistory

SESSION_TIMEOUT_SECONDS = 30 * 60  # 30 minutes

class SessionManager:
    def __init__(self):
        # sessions: session_id -> (ChatHistory, last_access_time)
        self.sessions: Dict[str, Tuple[ChatHistory, str]] = {}

        # intialize embedding model to embed user messages: one embedding model for all sessions
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

    # this method should be called everytime user calls the chat endpoint from the frontend
    def get_or_create_history(self, session_id: str) -> ChatHistory:
        '''
        Get an existing bot for the session or create a new one if it doesn't exist.

        Args:
            session_id (str): The unique identifier for the session. Maps to user id in database.

        Returns:
            InvestingChatBot: The bot instance associated with the session.
        '''
        now = time.time()
        # Clean up expired sessions
        self.cleanup_expired_sessions(now)
        if session_id in self.sessions:
            history, _ = self.sessions[session_id]
            self.sessions[session_id] = (history, now)  # update last access time
            return history
        else:
            history = ChatHistory(session_id=session_id, embeddings=self.embeddings)
            self.sessions[session_id] = (history, now)
            return history
        
    def clear_history(self, session_id: str):
        '''
        Clear the chat history for a given session.

        Args:
            session_id (str): The unique identifier for the session.

        Returns:
            None
        '''
        if session_id in self.sessions:
            history, _ = self.sessions[session_id]
            history.clear_history()

    def cleanup_expired_sessions(self, now: float):
        '''
        Clean up sessions that have not been accessed within the timeout period.

        Args:
            now (float): The current time in seconds since the epoch.

        Returns:
            None
        '''
        expired = [
            session_id
            for session_id, (_, last_access) in self.sessions.items()
            if now - last_access > SESSION_TIMEOUT_SECONDS
        ]
        for session_id in expired:
            # delete session from state
            del self.sessions[session_id]