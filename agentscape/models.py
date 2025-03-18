from enum import Enum


class ComponentType(str, Enum):
    """Type of component that can be installed."""

    AGENTS = "agents"
    TOOLS = "tools"
