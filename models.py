from enum import Enum
from typing import Annotated
from fastapi import Query
from pydantic import BaseModel


class Indicators(Enum):
    ON = "on"
    OFF = "off"
    BLINKING = "blinking"


class UserInput(BaseModel):
    user_id: int
    problem_description: Annotated[str, Query(max_length=300)]
    device_serial_number: Annotated[str, Query(min_length=64, max_length=64)]
    indicator_lights: Annotated[list[Indicators], Query(min_length=3, max_length=3)]


class ResponseData(BaseModel):
    response_status: str



