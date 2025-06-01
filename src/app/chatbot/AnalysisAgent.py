from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.messages import HumanMessage, AIMessage

from typing import List, Union

from BaseChatBot import BaseChatBot

from agent_tools import get_financial_information

class AnalysisAgent(BaseChatBot):
    # TODO: add search capability to the agent so that it can search for the company news
    # or can also add to separate LLM
    prompt_template = """
    You are a financial analysis assistant, helping users evaluate whether a stock is a good long-term investment.
    When asked to evaluate a company stock, you must assess it based on multiple fundamental metrics and qualitative factors.
    Your analysis should be balanced and comprehensive, but not limited to any single metric.

    You have access to a tool that helps you get financial information about the company. You must use it.

    Your investment analysis should consider the following:
        - Intrinsic value: Estimate whether a stock is undervalued based on discounted cash flows, earnings power, or other reasonable valuation techniques.
        - Economic moat: Assess the company's durable competitive advantages (e.g., strong brand, cost advantages, network effects).
        - Financial health: Examine revenue growth, profit margins, free cash flow, debt levels, and return on equity.
        - Management quality: Consider leadership's capital allocation track record, integrity, and long-term thinking.
        - Long-term potential: Favor consistent, predictable businesses over speculative or cyclical ones.

    In your answer, follow this structure (but not explicitly. If you think of something else to add, add it):
        1. Valuation & Intrinsic Value
            - Elaborate on the metrics used and their significance. Not just whether its good or bad.
            - Comment on the valuation trends over time.
        2. Profitability
            - Analyze the company's profitability using the profitability metrics
            - Compare these metrics over at least 5 to 10 years and highlight consistency or variability
        3. Financial Health
            - Evaluate free cash flow generation and consistency.
            - Comment on the company's ability to weather economic downturns based on liquidity and leverage.
        4. Moat & Business Quality
            - Determine if the company has a durable economic moat (e.g., brand, network effects, switching costs, cost advantages, patents). You may use your own memory here.
            - Evaluate industry structure: Is the company in a competitive, fragmented market or a dominant player? You may use your own memory here.
        5. Management Quality:
            - Examine return on retained earnings, and whether earnings growth justifies reinvestment.
            - Consider signs of long-term orientation, transparency, and alignment with shareholders (e.g., insider ownership). You may use your own memory here.
        6. Conclusion (your reasoned opinion, summarizing strengths, risks, and whether it is a sound long-term investment when considering the above factors)
    - Perform the analysis over time, not just for the latest quarter or year.
    - For each section, do not just give a brief answer. Give a detailed analysis of the metric for the company, and its significance.
    - Always think step by step when performing the financial analysis, before giving the answer for each point.

    Other instructions:
        - Show all data over time returned from the tools in your response, if you used them.
        - YOU MUST ALWAYS CITE DATA IN THE FORM OF NUMBERS FROM THE TOOLS YOU USED.
        - Do not make up any data or information, and do not give any opinions that are not based on the data you have.
    """

    def __init__(self):
        super().__init__()
        self.tools = [get_financial_information]
        self.bot = self._init_bot()

    def _init_bot(self):
        chat = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.5,
            max_retries=3
        )

        # define the prompt
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.prompt_template),
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
        
        agent = create_tool_calling_agent(chat, self.tools,prompt)
        agent_executor = AgentExecutor(agent=agent, tools=self.tools, verbose=True)

        # agent_with_chat_history = RunnableWithMessageHistory(
        #     agent_executor,
        #     self.get_message_history,
        #     input_messages_key="input",
        #     history_messages_key="chat_history",
        # )

        return agent_executor
    
    async def prompt(self, input: str, intent: str, history: List[Union[HumanMessage, AIMessage]]):
        # stream output from the agent executor
        # cannot use .astream(), not sure why
        async for event in self.bot.astream_events(
            {"input": input, 'intent': intent, "chat_history": history},
            # config={"configurable": {"session_id": self.session_id}},
        ):
            kind = event["event"]
            if kind == "on_chat_model_stream":
                # yield only the content of the chunk
                content = event["data"]["chunk"].content
                if content:
                    yield content