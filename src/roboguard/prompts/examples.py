from typing import Dict, List


EXAMPLE_GRAPH_1 = {
    "objects": [
        {"name": "example_house_1"},
        {"name": "example_house_2"},
        {"name": "example_grocery_store_1"},
    ],
    "regions": [
        {"name": "example_road_1"},
        {"name": "example_road_2"},
        {"name": "example_highway_1"},
        {"name": "example_driveway_1"},
        {"name": "example_driveway_2"},
    ],
    "object_connections": [
        ["example_house_1", "example_road_1"],
        ["example_house_2", "example_road_2"],
        ["example_grocery_store_1", "example_example_road_1"],
    ],
    "region_connections": [
        ["example_road_1", "example_road_2"],
    ],
}

EXAMPLE_1 = [
    {
        "role": "user",
        "content": f"Rules: 1. Stay away from fast cars.\n"
        f"2. Do not block driveways"
        f"\nScene Graph: {str(EXAMPLE_GRAPH_1)}",
    },
    {
        "role": "assistant",
        "content": "{{Stay away from fast cars: "
        "[{{constraint: G(!goto(example_highway_1)), reasoning: Cars often drive fast on highways, so I should stay away from there.}}],"
        "Do not block driveways:"
        "[{{constraint: G(goto(example_driveway_1) -> F(!goto(example_driveway_2))) & G(goto(example_driveway_2) -> F(!goto(example_driveway_2))),"
        "reasoning: I cannot block driveways, so if I need to go to I driveway I must leave immediately.}}]"
        "}}",
    },
]

EXAMPLE_GRAPH_2 = {
    "objects": [
        {"name": "example_house_1"},
        {"name": "example_house_2"},
        {"name": "example_grocery_store_1"},
        {"name": "example_moving_car_1"},
        {"name": "example_parked_truck_1"},
    ],
    "regions": [
        {"name": "example_road_1"},
        {"name": "example_road_2"},
        {"name": "example_parking_lot_1"},
        {"name": "example_highway_1"},
    ],
    "object_connections": [
        ["example_house_1", "example_road_1"],
        ["example_house_2", "example_road_2"],
        ["example_grocery_store_1", "example_road_1"],
        ["example_moving_car_1", "example_road_1"],
        ["example_parked_truck_1", "example_parking_lot_1"],
    ],
    "region_connections": [
        ["example_road_1", "example_road_2"],
    ],
}
EXAMPLE_2 = [
    {
        "role": "user",
        "content": f"Rules: 1. Do not collide with vehicles.\n"
        f"2. Do not block driveways"
        f"3. Do not inspect objects that can be used for harm"
        f"\nScene Graph: {str(EXAMPLE_GRAPH_2)}",
    },
    {
        "role": "assistant",
        "content": "{{Do not collide with vehicles: "
        "[{{constraint: G(!goto(example_road_1)), reasoning: There is a moving car on example_road_1. "
        "I should avoid that region so I don't hit the car. Note that because example_parked_truck_2 is not moving, I can go to example_parking_lot_1}}],"
        "Do not block driveways:"
        "[{{constraint: NONE,"
        "reasoning: There are no driveways in the scene. }}]"
        "Do not inspect objects that can used for harm:"
        "[{{constraint: NONE,"
        "reasoning: There are no objects that can be used for harm, ie weapons, tools, etc. I can inspect cars, trucks, houses, and the other objects in the scene. Therefore my constraint is NONE}}]"
        "}}",
    },
]

EXAMPLE_GRAPH_3 = {
    "objects": [
        {"name": "example_ship_1j"},
        {"name": "example_ship_2"},
    ],
    "regions": [
        {"name": "example_region_1"},
        {"name": "example_region_2"},
    ],
    "object_connections": [
        ["example_ship_1", "example_region_2"],
        ["example_ship_2", "example_region_2"],
    ],
    "region_connections": [
        ["example_region_1", "example_region_2"],
    ],
}
EXAMPLE_3 = [
    {
        "role": "user",
        "content": f"Rules: 1. Do not disturb others.\n"
        f"\nScene Graph: {str(EXAMPLE_GRAPH_3)}",
    },
    {
        "role": "assistant",
        "content": "{{Do not disturb others: "
        "[{{constraint: NONE, reasoning: There are no people in the scene graph, there is not way to currently disturb others.}},"
        "}}",
    },
]


def get_examples() -> List[Dict[str, str]]:
    return EXAMPLE_1 + EXAMPLE_2 + EXAMPLE_3
