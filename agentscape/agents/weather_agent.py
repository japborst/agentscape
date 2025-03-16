from agents import Agent, function_tool


@function_tool
def get_weather(city: str) -> str:
    return f"The weather in {city} is sunny."


weather_agent = Agent(
    name="Weather agent",
    instructions="You are a helpful assistant providing weather information.",
    tools=[get_weather],
)
