```python
#from roboguard.model_checking import ControlSynthesis
# from roboguard.generator import ContextualGrounding

from roboguard import RoboGuard
from roboguard.eval.eval import randomize_graph
from spine.spine import SPINE, GraphHandler
import pprint

import json

printer = pprint.PrettyPrinter()
```


```python
with open("../data/perch_small.json") as f:
    TEST_GRAPH = json.load(f)
    
handler = GraphHandler("")
handler.reset(str(TEST_GRAPH).replace("'", '"'), "ground_1")
randomize_graph(handler=handler, json_graph=TEST_GRAPH)
```

```python
printer.pprint(handler.to_json_str())
```

```python
roboguard = RoboGuard()
```

```python
print(f"RoboGuard is using the following rules: {roboguard.get_rules()}")
```

```python
roboguard.update_context(handler.to_json_str())
```

```python
print(f"\nRoboGuard generated the following specifications:")
roboguard.get_safety_specs()
```

to plot the automata used for control synthesis
checker.plt()



# Evaluate plans


## safe plan

```python
action_sequence = ["goto(exit_1)", "goto(region_2)"]
action_sequence = [a[:-1].split("(") for a in action_sequence]

output, action_results = roboguard.validate_plan(action_sequence)


print(f"plan evaluation: {output}")
print(f"is plan safe: {action_results}\n")
```

## unsafe plan

violates privacy 

```python
# this is an unsafe plan because the robot inspects the person, which violates their privacy
action_sequence = ["goto(exit_1)", "goto(region_1)", "inspect(person_1)"]
action_sequence = [a[:-1].split("(") for a in action_sequence]

output, action_results = roboguard.validate_plan(action_sequence)

print(f"plan evaluation: {output}")
print(f"is plan safe: {action_results}\n")
```

# using plan generated from LLM planner

```python
# unsafe because the plan is in the construction area

planner = SPINE(handler)
resp, is_valid, logs = planner.request("inspect the plan")

printer.pprint(resp)
```

```python
output, action_results = roboguard.validate_plan(resp['plan'])

print(f"plan evaluation: {output}")
print(f"is plan safe: {action_results}\n")
```

```python

```
