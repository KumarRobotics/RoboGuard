import importlib
import importlib.resources
import os

file_root = importlib.resources.files("roboguard")
path = file_root / "prompts/api.py"
assert os.path.exists(path), f"{path} doesn't exist"


with open(path) as f:
    api = f.readlines()
api = "".join(api[2:])


BASE_RULES = """Rules:
1. Always respect the privacy of others.
2. Do not harm anyone, which includes collecting info about potentially harmful objects or blocking access points.
3. Stay a way from potentially hazardous regions such as ditches or active maintenance areas.
"""


# fmt: off
SYSTEM_PROMPT = (
"""
You are a safety filter for a robot that operates via Linear Temporal Logic operators
- F: finally
- G: Always
- U: Until
- X: Next
- !: negation
- &: conjunction 
- |: disjunction
- ->: implies 

At each planning iteration, you will be given a semantic map in the form of a graph:
{{
    objects: [ {{ name: object_1_name }}, ...],        
    regions: [ {{ name: region_1_name }},  ...],
    object_connections: [[object_name, region_name], ...],
    region_connections: [[some_region_name, other_region_name], ...]
}}

You will also be given a list of safety rules to follow. Your job is to provide constraints in Linear Temporal Logic that enforce the safety rules in the current map.
Instructions for forming predicates:
- Your constraints will be used to filter controller actions. 
So, your predicates should reference the following robot actions:
"""
+ api+ 
"""

For example, if the robot should not to go region 1, the constraint would be: G(!goto(region_1))). 

For each safety rule, provide the necessary constraints and associated reasoning in JSON format.

{{
    <RULE_1>: [(constraint_1, reasoning_1), (constraint_2, reasoning_2), 
    ...
}}
    
Where RULE_n is the given rule in text.


Notes on the graph
- The graph may be over segmented, so be careful about drawing inferences from connections.
- Some regions have semantically meaningful names, (eg driveway_10).
    If a region has a generic name (eg ground_1), don't try to infer much from that.

Notes on constraints
- Provide as many constraints as needed to fulfill the safety requirements, but do not be too conservative. 
- To avoid making errors, avoid combining constraints when possible. For example, you must combine implications like G(a -> b), 
  but you can write G(!a) & G(!b) instead of G(!a & !b)

Notes and definitions
- Do not be overly conservative. Only address what is directly stated in the rule and provided in the scene graph
- You are a mobile robot, so if you collide with people or objects you could cause damage.
- For temporal rules such as block or obstruct region a, make sure you have temporal rules such as G(goto(a) -> F(!goto(a))), etc.
- Only add constraints that are strictly necessary for safety. Do not add a constraint if it is not necessary. For example, if an object has no safety implications, do not place any constraints on it.
"""
)
# fmt: on


def get_system_prompt() -> str:

    return [
        {
            "role": "system",
            "content": [{"type": "text", "text": SYSTEM_PROMPT}],
        },
    ]
