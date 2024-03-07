from enum import Enum
from typing import Annotated
from fastapi import Query
from pydantic import BaseModel
from database import Base
from sqlalchemy.orm import relationship

from sqlalchemy import Column, Integer, String, Date, ForeignKey


class Indicators(Enum):
    ON = "on"
    OFF = "off"
    BLINKING = "blinking"


class UserInput(BaseModel):
    user_id: int
    problem_description: Annotated[str, Query(max_length=300)]
    device_serial_number: Annotated[str, Query(min_length=64, max_length=64)]
    indicator_lights: Annotated[list[Indicators], Query(min_length=3, max_length=3)]

class IndicatorList(Base):
    __tablename__ = 'indicators'

    id = Column(Integer, primary_key=True, index=True)
    form_input_id = Column(Integer, ForeignKey('formInput.form_input_id'), unique=True)  # One-to-one relationship
    indicator1 = Column(String)
    indicator2 = Column(String)
    indicator3 = Column(String)

    formInput = relationship("FormInput", back_populates="indicators", uselist=False)


class FormInput(Base):
    __tablename__ = 'formInput'

    form_input_id = Column(Integer, primary_key=True, index=True)
    indicator_list_id = Column(Integer, ForeignKey('indicators.id'), unique=True)
    user_id = Column(Integer)
    problem_description = (String(300))
    device_serial_number = (String(64))

    form = relationship("Form", back_populates="formInput")
    indicators = relationship("IndicatorList", back_populates="formInput", uselist=False)


class Form(Base):
    __tablename__ = 'form'

    form_id = Column(Integer, primary_key=True, index=True)
    form_input_id = Column(Integer, ForeignKey('formInput.form_input_id'))
    date = Column(Date)
    response_status = Column(String(100))

    formInput = relationship("FormInput", back_populates="form")






