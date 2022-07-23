from __future__ import annotations
from datetime import time
from typing import NamedTuple


class UserParametersType(NamedTuple):
    name: str
    sending_time: time


class UserType(NamedTuple):
    id: int
    parameters: UserParametersType
