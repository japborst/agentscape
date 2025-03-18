from agents import Agent

from .tools.get_weather import get_weather

weather_agent = Agent(
    name="Weather agent",
    instructions="You are a helpful assistant providing weather information.",
    tools=[get_weather],
)
