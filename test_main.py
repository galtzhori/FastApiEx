from unittest import TestCase
import main
from main import app
from fastapi.testclient import TestClient
from models import Indicators

valid_serial_number_length = "1234567890123456789012345678901234567890123456789012345678901234"
serial_number_length_60 = "567890123456789012345678901234567890123456789012345678901234"
url = "https://127.0.0.1:8000/process_input/"

client = TestClient(app)


class TestProcessInput(TestCase):
    def valid_input_with_prefix_and_indicators(self, prefix: str, message: str, indicator1=Indicators.ON,
                                               indicator2=Indicators.ON,
                                               indicator3=Indicators.ON):
        response = client.post(url,
                               json={"user_id": 0, "problem_description": "",
                                     "device_serial_number": prefix + serial_number_length_60,
                                     "indicator_lights": [indicator1.value, indicator2.value, indicator3.value]})
        self.assertEqual(response.status_code, 200,
                         "input's type is valid")
        self.assertEqual(response.text.split("\"")[1], message,
                         "response message should be: " + message)

    def test_bad_input_types(self):
        # device_serial_number not a string
        response = client.post(url,
                               json={"user_id": 0, "problem_description": "", "device_serial_number": 0,
                                     "indicator_lights": ["on", "on", "on"]})
        self.assertEqual(response.status_code, 422, "device_serial_number should not accept int input")

        # invalid indicator_lights number
        response = client.post(url,
                               json={"user_id": 0, "problem_description": "",
                                     "device_serial_number": valid_serial_number_length,
                                     "indicator_lights": ["on", "on"]})
        self.assertEqual(response.status_code, 422,
                         "indicator_lights should not accept input length that is less than 3 objects")

        # invalid indicator_lights input
        response = client.post(url,
                               json={"user_id": 0, "problem_description": "",
                                     "device_serial_number": valid_serial_number_length,
                                     "indicator_lights": ["hi", "yo", "off"]})
        self.assertEqual(response.status_code, 422,
                         "indicator_lights should be one of: off/on/blinking")

    def test_device_serial_number_24_X(self):
        prefix = "24-X"
        # invalid indicator_lights input
        self.valid_input_with_prefix_and_indicators(prefix,main.upgrade_message)

    def test_device_serial_number_36_X(self):
        prefix = "36-X"
        # serial number starts with prefix and 3 indicators are off
        self.valid_input_with_prefix_and_indicators(prefix, main.turn_on_message, Indicators.OFF, Indicators.OFF,
                                                    Indicators.OFF)
        # serial number starts with prefix and any 2 indicators are blinking
        self.valid_input_with_prefix_and_indicators(prefix, main.blinking_indicator, Indicators.BLINKING,
                                                    Indicators.OFF,
                                                    Indicators.BLINKING)
        self.valid_input_with_prefix_and_indicators(prefix, main.blinking_indicator, Indicators.BLINKING,
                                                    Indicators.BLINKING,
                                                    Indicators.OFF)
        self.valid_input_with_prefix_and_indicators(prefix, main.blinking_indicator, Indicators.OFF,
                                                    Indicators.BLINKING,
                                                    Indicators.BLINKING)
        # serial number starts with prefix and all 3 indicators are on
        self.valid_input_with_prefix_and_indicators(prefix, main.on_indicator, Indicators.ON, Indicators.ON,
                                                    Indicators.ON)
        # serial number starts with prefix and indicators dont predict the outcome
        self.valid_input_with_prefix_and_indicators(prefix, main.default_message, Indicators.BLINKING, Indicators.ON,
                                                    Indicators.ON)
        self.valid_input_with_prefix_and_indicators(prefix, main.default_message, Indicators.OFF, Indicators.BLINKING,
                                                    Indicators.ON)

    def test_device_serial_number_51_B(self):
        prefix = "51-B"
        # serial number starts with prefix and 3 indicators are off
        self.valid_input_with_prefix_and_indicators(prefix, main.turn_on_message, Indicators.OFF, Indicators.OFF,
                                                    Indicators.OFF)
        # serial number starts with prefix and any indicator is blinking
        self.valid_input_with_prefix_and_indicators(prefix, main.blinking_indicator, Indicators.BLINKING,
                                                    Indicators.OFF,
                                                    Indicators.ON)
        self.valid_input_with_prefix_and_indicators(prefix, main.blinking_indicator, Indicators.BLINKING,
                                                    Indicators.BLINKING,
                                                    Indicators.OFF)
        self.valid_input_with_prefix_and_indicators(prefix, main.blinking_indicator, Indicators.OFF,
                                                    Indicators.OFF,
                                                    Indicators.BLINKING)
        # serial number starts with prefix and and atleast one indicator is on, and none are blinking
        self.valid_input_with_prefix_and_indicators(prefix, main.on_indicator, Indicators.ON, Indicators.ON,
                                                    Indicators.ON)
        self.valid_input_with_prefix_and_indicators(prefix, main.on_indicator, Indicators.ON, Indicators.OFF,
                                                    Indicators.OFF)

    def test_device_serial_number_is_number(self):
        prefix = "1984"
        self.valid_input_with_prefix_and_indicators(prefix, main.serial_number_is_digits)

    def test_unknown_device(self):
        self.valid_input_with_prefix_and_indicators("24-K", main.unknown_message)
        self.valid_input_with_prefix_and_indicators("52-B", main.unknown_message)



