from __future__ import annotations
from typing import NamedTuple
from aiogram.types import Message


class UserParametersType(NamedTuple):
    name: str
    sending_time: str


class UserType(NamedTuple):
    id: int
    parameters: UserParametersType
    
def make_user_from_message(message: Message, sending_time: str) -> UserType:
    user = UserType(message.from_user.id, UserParametersType(message.from_user.username, sending_time))
    return user
