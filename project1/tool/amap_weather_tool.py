
from langchain.tools import tool


@tool
def amap_weather_tool(location: str) -> str:
    """Get the weather in a location.

    Args:
        location: The name of the location to get weather for
    """
    return f"The weather in {location} is sunny with a temperature of 22 degrees."


class AmapWeatherTool:
    @staticmethod
    def get_tool():
        return amap_weather_tool
