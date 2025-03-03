from enums.enums import ChatRole, TextAlignment, TextColor
from .base import BaseModel
from sqlalchemy import Column, Integer, ForeignKey

from rich.panel import Panel
from rich.text import Text
from rich.align import Align

from .chat import Chat
from .chat_message import ChatMessage


class Conversation(BaseModel):
    __tablename__ = 'conversation'

    agent_1_chat_id = Column(Integer, ForeignKey('chat.id'), nullable=False)
    agent_2_chat_id = Column(Integer, ForeignKey('chat.id'), nullable=False)

    def __init__(self, agent_1_chat_id: int, agent_2_chat_id: int) -> None:
        super().__init__()
        self.agent_1_chat_id = agent_1_chat_id
        self.agent_2_chat_id = agent_2_chat_id

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'agent_1_id': self.agent_1_chat_id,
            'agent_2_id': self.agent_2_chat_id,
            'created_at': self.created_at,
        }

    @property
    def agent_1_chat(self) -> Chat:
        return Chat.get_one(id=self.agent_1_chat_id)

    @property
    def agent_2_chat(self) -> Chat:
        return Chat.get_one(id=self.agent_2_chat_id)

    @property
    def merged_chat_history(self) -> list[ChatMessage]:
        message = ChatMessage.get_multiple(
            chat_id=[self.agent_1_chat_id, self.agent_2_chat_id], role=[ChatRole.ASSISTANT, ChatRole.SYSTEM]
        )
        return message

    def generate_chat_bubble(self, chat_message: ChatMessage) -> Align:
        assert chat_message.chat_id == self.agent_1_chat_id or chat_message.chat_id == self.agent_2_chat_id, (
            'must be a message from any of the conversation chats.'
        )

        chat_bubble = self.generate_empty_chat_bubble(chat_message.chat)
        panel = chat_bubble.renderable

        if chat_message.role == ChatRole.SYSTEM:
            color = TextColor.SYSTEM_COLOR
            panel.border_style = color.value
            if chat_message.chat_id == self.agent_1_chat_id:
                panel.title = 'Agent 1 (SYSTEM)'
            else:
                panel.title = 'Agent 2 (SYSTEM)'

        panel.renderable = Text(chat_message.content, justify=TextAlignment.LEFT.value)

        return chat_bubble

    def generate_empty_chat_bubble(self, chat: Chat) -> Align:
        assert chat.id == self.agent_1_chat_id or chat.id == self.agent_2_chat_id, (
            'must be a message from any of the conversation chats.'
        )

        sender = chat.default_model
        align = TextAlignment.RIGHT if chat.id == self.agent_1_chat_id else TextAlignment.LEFT

        if chat.id == self.agent_1_chat_id:
            color = TextColor.AGENT_1_COLOR
            sender = f'Agent 1 ({sender})'
        else:
            color = TextColor.AGENT_2_COLOR
            sender = f'Agent 2 ({sender})'

        chat_bubble = Panel(
            Text('Loading...', justify=TextAlignment.LEFT.value),
            title=sender,
            title_align=align.value,
            border_style=color.value,
            padding=(1, 2),
            expand=False,
        )

        if chat.id == self.agent_1_chat_id:
            return Align.right(chat_bubble)

        return Align.left(chat_bubble)
