from abc import ABC, abstractmethod
from typing import List

class BaseChatBot(ABC):
    prompt_template: str
    tools: list

    @abstractmethod
    async def prompt(self, input: str, history: List):
        pass

    @abstractmethod
    def _init_bot(self):
        pass