from typing import List

# Safety filter generates constraints assuming the robot plans using this API


def goto(region_node: str) -> None:
    """Navigate to `region_node`.
    This function uses a graph-search algorithm to
    find the most efficient path to that node."""


def map_region(region_node: str) -> List[str]:
    """Navigate to region in the graph and look for new objects.
    Will return updates to graph (if any).
    """


def explore_region(region_node: str, exploration_radius_meters: float) -> List[str]:
    """Explore within `exploration_radius_meters`
    around `region_node`
    Will return updates to graph (if any).
    """


def extend_map(x_coordinate: int, y_coordinate: int) -> List[str]:
    """Try to add region node to graph at the coordinates
    (x_coordinate, y_coordinate).
    Will return updates to graph (if any).
    """


def replan() -> None:
    """You will update your plan with newly acquired information.
    This is a placeholder command, and cannot be directly executed.
    """


def inspect(object_node: str, vlm_query: str) -> List[str]:
    """Gather more information about `object_node` by
    querying a vision-language model with `vlm_query`.
    Be concise in your query. The robot will also navigate
    to the region connected to `object_node`.
    Will return updates to graph (if any).
    """


def answer(answer: str) -> None:
    """Provide an answer to the instruction"""


def clarify(question: str) -> None:
    """Ask for clarification.
    Only ask if the instruction is too vague to make a plan."""
