import time
from app.backend.chatbot.InvestingChatBot import InvestingChatBot

SESSION_TIMEOUT_SECONDS = 30 * 60  # 30 minutes

class SessionManager:
    def __init__(self):
        # sessions: session_id -> (InvestingChatBot, last_access_time)
        self.sessions = {}

    # this method should be called everytime user calls the chat endpoint from the frontend
    def get_or_create_bot(self, session_id: str) -> InvestingChatBot:
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
            bot, _ = self.sessions[session_id]
            self.sessions[session_id] = (bot, now)  # update last access time
            return bot
        else:
            bot = InvestingChatBot(session_id=session_id)
            self.sessions[session_id] = (bot, now)
            return bot

    def remove_bot(self, session_id: str) -> None:
        '''
        Remove the bot associated with the session ID.

        Args:
            session_id (str): The unique identifier for the session.

        Returns:
            None
        '''
        if session_id in self.sessions:
            del self.sessions[session_id]

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
            del self.sessions[session_id]