from enum import Enum


class ChatRole(Enum):
    SYSTEM = 'system'
    ASSISTANT = 'assistant'
    USER = 'user'

    def is_system(self) -> bool:
        return self == ChatRole.SYSTEM

    def is_assistant(self) -> bool:
        return self == ChatRole.ASSISTANT

    def is_user(self) -> bool:
        return self == ChatRole.USER


class TextAlignment(Enum):
    RIGHT = 'right'
    CENTER = 'center'
    LEFT = 'left'

    def is_right(self) -> bool:
        return self == TextAlignment.RIGHT

    def is_center(self) -> bool:
        return self == TextAlignment.CENTER

    def is_left(self) -> bool:
        return self == TextAlignment.LEFT


class TextColor(Enum):
    AGENT_1_COLOR = 'green'
    SYSTEM_COLOR = 'red'
    AGENT_2_COLOR = 'cyan'

    def is_agent_1_color(self) -> bool:
        return self == TextColor.AGENT_1_COLOR

    def is_system_color(self) -> bool:
        return self == TextColor.SYSTEM_COLOR

    def is_agent_2_color(self) -> bool:
        return self == TextColor.AGENT_2_COLOR
