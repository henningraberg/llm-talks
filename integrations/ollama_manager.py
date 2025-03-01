from typing import Generator, Optional

import ollama

from models.chat import Chat
from models.chat_message import ChatMessage

from enums.enums import ChatRole


class OllamaManager:
    def __init__(self):
        pass

    @staticmethod
    def get_downloaded_models() -> ollama.ListResponse:
        return ollama.list()

    @staticmethod
    def get_model_information(model: str) -> ollama.ShowResponse:
        return ollama.show(model=model)

    @staticmethod
    def download_model(model: Optional[str] = None) -> Generator:
        for x in ollama.pull(model=model, stream=True):
            yield x

    @staticmethod
    def delete_model(model: str) -> ollama.StatusResponse:
        return ollama.delete(model=model)

    @staticmethod
    def chat(sender_agent_chat: Chat, responder_agent_chat: Chat) -> Generator:
        message_history = sender_agent_chat.get_chat_history_as_dict()

        ai_response = ''
        for chunked_response in ollama.chat(
            messages=message_history, stream=True, model=sender_agent_chat.default_model
        ):
            ai_response += chunked_response.message.content
            yield chunked_response.message.content

        ChatMessage(
            chat_id=sender_agent_chat.id,
            role=ChatRole.ASSISTANT,
            model=sender_agent_chat.default_model,
            content=ai_response,
        ).save()

        ChatMessage(
            chat_id=responder_agent_chat.id,
            role=ChatRole.USER,
            model=responder_agent_chat.default_model,
            content=ai_response,
        ).save()

    @staticmethod
    def chat_gui(chat: Chat) -> Generator:
        message_history = chat.get_chat_history_as_dict()
        ai_response = ChatMessage(chat_id=chat.id, role=ChatRole.ASSISTANT, model=chat.default_model, content='')
        for chunked_response in ollama.chat(messages=message_history, stream=True, model=chat.default_model):
            ai_response.content += chunked_response.message.content
            yield chunked_response.message.content

        ai_response.save()

    @staticmethod
    def generate_chat_name(chat: Chat) -> str:
        message_history = chat.get_chat_history_as_dict()
        message_history.append(
            ChatMessage(
                chat_id=chat.id,
                role=ChatRole.USER,
                model=chat.default_model,
                content='Based on your last response generate a name for this chat.'
                'Respond with only the name and nothing else.'
                'Do not include any extra words, explanations, or formatting—just the name.'
                'If you include anything other than the name, the response is invalid.',
            ).to_dict()
        )
        return ollama.chat(messages=message_history, model=chat.default_model).message.content
