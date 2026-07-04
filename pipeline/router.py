from pipeline.data.weather import get_weather
from pipeline.data.mandi import get_mandi_price
from pipeline.data.schemes import get_scheme_info
from pipeline.data.advisory import get_advisory


def route(intent: dict) -> dict:
    """
    Input : intent dict from intent.py.
    Output: raw data dict from the matching data source, passed straight
            to answer.py.
    """
    question_type = intent.get("question_type", "advisory")
    crop = intent.get("crop")
    location = intent.get("location")
    situation = intent.get("situation")

    print(f"Router       : question_type={question_type}, crop={crop}, location={location}")

    if question_type == "price":
        return get_mandi_price(crop, location)
    if question_type == "weather":
        return get_weather(location)
    if question_type == "scheme":
        return get_scheme_info(situation)
    return get_advisory(crop, situation)
