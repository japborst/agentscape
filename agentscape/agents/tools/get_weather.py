from agents import function_tool


@function_tool
def get_weather(city: str) -> str:
    return f"The weather in {city} is sunny."
