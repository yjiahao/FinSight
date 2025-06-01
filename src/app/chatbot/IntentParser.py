from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser

from BaseChatBot import BaseChatBot

class IntentParser(BaseChatBot):
    prompt_template = '''

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

    def __init__(self):
        super().__init__()
        self.tools = [] # no need tools for intent parsing
        self.bot = self._init_bot()

    def _init_bot(self):
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0,
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.prompt_template),
                ("human", "{input}"),
            ]
        )

        parser = JsonOutputParser()

        chain = prompt | llm | parser

        return chain
    
    def prompt(self, input: str):
        # stream output from the bot
        response = self.bot.invoke({"input": input})
        return response