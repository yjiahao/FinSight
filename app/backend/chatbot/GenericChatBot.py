from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from .BaseChatBot import BaseChatBot

# Generic chatbot class that can answer a wide range of questions
class GenericChatBot(BaseChatBot):
    # TODO: improve on the prompt template to be more specific or useful
    prompt_template = '''
    You are a helpful chatbot that helps users with their questions and queries.
    You can answer questions about a wide range of topics from the user.
    '''

    def __init__(self):
        super().__init__()
        self.tools = []
        self.bot = self._init_bot()

    def _init_bot(self):
        chat = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.5,
            max_retries=3
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.prompt_template),
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
    
    async def prompt(self, input: str, intent: str, history: list):
        async for token in self.bot.astream(
            {
                "input": input,
                "intent": intent,
                "chat_history": history
            }
        ):
            # the token is of type AIMessage
            yield token.content