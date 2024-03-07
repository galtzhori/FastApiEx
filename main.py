from fastapi import FastAPI, Depends
from datetime import datetime
from database import engine, SessionLocal
from models import UserInput, Indicators
from sqlalchemy.orm import Session

import models

################# RETURN MESSAGES ################
serial_number_is_digits = "Bad serial number"
unknown_message = "Unknown device"
upgrade_message = "please upgrade your device"
turn_on_message = "turn on the device"
blinking_indicator = "Please wait"
on_indicator = "ALL is ok"
default_message = "I havent been told what to do in this case"
##################################################


app = FastAPI()
models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/process_input/")
async def process_input(user_input: UserInput, db: Session = Depends(get_db)) -> str:
    # Logic for calculating response status
    input_processor = ProcessInput(user_input)
    response = input_processor.check_serial_number()
    # update database
    upload_to_database(user_input, response, db)
    # Return response data
    return response


def upload_to_database(user_input: UserInput, response: str, db: Session = Depends(get_db)):
    indicators = models.IndicatorList(indicator1=user_input.indicator_lights[0].value,
                                      indicator2=user_input.indicator_lights[1].value,
                                      indicator3=user_input.indicator_lights[2].value)
    db.add(indicators)
    db.commit()

    form_input = models.FormInput(user_id=user_input.user_id, problem_description=user_input.problem_description,
                                  device_serial_number=user_input.device_serial_number, indicator_list_id=indicators.id)
    db.add(form_input)
    db.commit()
    form_input_object = db.query(models.FormInput).filter(
        models.FormInput.form_input_id == form_input.form_input_id).first()
    indicators.form_input_id = form_input_object.form_input_id
    db.add(form_input)
    db.commit()
    form = models.Form(date=datetime.now(), response_status=response.split("\"")[1],
                       form_input_id=form_input.form_input_id)
    db.add(form)
    db.commit()
    # db.close()


class ProcessInput:
    def __init__(self, user_input: UserInput):
        self.user_input = user_input
        self.indicators_amount = {}
        for indicator in user_input.indicator_lights:
            self.indicators_amount.update({indicator: self.indicators_amount.get(indicator, 0) + 1})

    def check_serial_number(self) -> str:
        if self.user_input.device_serial_number.isdigit():
            return serial_number_is_digits
        prefix = self.user_input.device_serial_number[0:4]
        if prefix == "24-X":
            return upgrade_message
        elif prefix == "36-X":
            return self.process_indicators(len(Indicators), 2, len(Indicators))
        elif prefix == "51-B":
            return self.process_indicators(len(Indicators), 1, 1)
        return unknown_message

    def process_indicators(self, min_off: int, min_blinking: int, min_on: int) -> str:
        if self.indicators_amount.get(Indicators.OFF, 0) == min_off:
            return turn_on_message
        elif self.indicators_amount.get(Indicators.BLINKING, 0) >= min_blinking:
            return blinking_indicator
        elif self.indicators_amount.get(Indicators.ON, 0) >= min_on:
            return on_indicator
        return default_message
