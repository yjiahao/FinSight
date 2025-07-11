from .AnalysisAgent import AnalysisAgent
from .ChatHistory import ChatHistory
from .GenericChatBot import GenericChatBot
from .IntentParser import IntentParser
from .SearchAgent import SearchAgent
from .TutorAgent import TutorAgent

# main class that integrates all components of the investing chatbot
class InvestingChatBot:
    def __init__(self):

        self.intent_parser = IntentParser()
        self.search_agent = SearchAgent()
        self.analysis_agent = AnalysisAgent()
        self.tutor_chatbot = TutorAgent()
        self.generic_chatbot = GenericChatBot()

    async def prompt(self, message: str, chat_history: ChatHistory):
        '''Process a user message and return the AI's response based on the intent and chat history.'''
        # get intent of the message
        intent = self.intent_parser.prompt({"input": message})

        # get chat history
        history = chat_history.retrieve(message)

        # decide which chatbot to use based on the intent
        chatbot = None
        if intent['topic'] == 'search':
            chatbot = self.search_agent
        elif intent['topic'] == 'stock_analysis':
            chatbot = self.analysis_agent
        elif intent['topic'] == 'learn_investing':
            chatbot = self.tutor_chatbot
        else:
            chatbot = self.generic_chatbot

        # call the chatbot's prompt method
        ai_response_string = ""
        async for token in chatbot.prompt(
            input=message,
            intent=intent['topic'],
            history=history
        ):
            ai_response_string += token
            yield token

        # add messages to chat history
        await chat_history.add_messages(
            messages=[message, ai_response_string],
            metadata=[
                {"sender": "human"},
                {"sender": "ai"}
            ]
        )