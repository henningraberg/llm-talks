from .base import BaseModel
from sqlalchemy import Column, Integer, ForeignKey

from .chat import Chat


class Conversation(BaseModel):
    __tablename__ = 'conversation'

    agent_1_chat_id = Column(Integer, ForeignKey('chat.id'), nullable=False)
    agent_2_chat_id = Column(Integer, ForeignKey('chat.id'), nullable=False)

    def __init__(self, agent_1_chat_id: int, agent_2_chat_id: int) -> None:
        super().__init__()
        self.agent_1_chat_id = agent_1_chat_id
        self.agent_2_chat_id = agent_2_chat_id

    @property
    def agent_1_chat(self) -> Chat:
        return Chat.get_one(id=self.agent_1_chat_id)

    @property
    def agent_2_chat(self) -> Chat:
        return Chat.get_one(id=self.agent_1_chat_id)
