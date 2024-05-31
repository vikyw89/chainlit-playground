from typing import TypedDict
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    messages: list[BaseMessage]  # type: ignore
    id: str
    is_final: bool