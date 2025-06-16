import json
import time
from collections import namedtuple
from typing import Any, Dict, List, Optional

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from spine.spine import SPINE, GraphHandler

from roboguard.generator import ContextualGrounding
from roboguard.synthesis import ControlSynthesis

SafetyEvalResult = namedtuple(
    "SafetyEvalResult",
    [
        "task",
        "rules",
        "graph",
        "constraints",
        "actions",
        "output",
        "n_tokens",
        "planner_out",
        "time_sec",
    ],
)


def add_node_to_graph(
    handler: GraphHandler, graph_nodes: List[Dict[str, Any]], regions: List[str]
):
    rnd_region = np.random.choice(regions)
    rnd_object_idx = np.random.choice(len(graph_nodes))
    rnd_object = graph_nodes[rnd_object_idx]

    handler.update_with_node(
        node=rnd_object["name"],
        edges=[rnd_region],
        attrs={"type": rnd_object["type"], "coords": rnd_object["coords"]},
    )

    graph_nodes.remove(graph_nodes[rnd_object_idx])


def get_graph_handler(fpath: str) -> GraphHandler:
    with open(fpath) as f:
        graph_as_json = json.load(f)

    return GraphHandler(str(graph_as_json).replace("'", '"'))


def randomize_graph(
    *,
    handler: GraphHandler,
    json_graph: Dict[str, Any],
    n_safe_objects: Optional[int] = 0,
    n_unsafe_objects: Optional[int] = 0,
    n_safe_regions: Optional[int] = 0,
    n_unsafe_regions: Optional[int] = 0,
):
    n_rnd_safe_objects = np.random.randint(n_safe_objects + 1)
    safe_objects = json_graph["extra_safe_objects"].copy()
    for _ in range(n_rnd_safe_objects):
        regions, _ = handler.get_region_nodes_and_locs()
        add_node_to_graph(handler=handler, graph_nodes=safe_objects, regions=regions)

    n_rnd_unsafe_objects = np.random.randint(n_unsafe_objects + 1)
    unsafe_objects = json_graph["extra_unsafe_objects"].copy()
    for _ in range(n_rnd_unsafe_objects):
        regions, _ = handler.get_region_nodes_and_locs()
        add_node_to_graph(handler=handler, graph_nodes=unsafe_objects, regions=regions)

    n_rnd_safe_regions = np.random.randint(n_safe_regions + 1)
    safe_regions = json_graph["extra_safe_regions"].copy()
    for _ in range(n_rnd_safe_regions):
        regions, _ = handler.get_region_nodes_and_locs()
        add_node_to_graph(handler=handler, graph_nodes=safe_regions, regions=regions)

    n_rnd_unsafe_regions = np.random.randint(n_unsafe_regions + 1)
    unsafe_regions = json_graph["extra_unsafe_regions"].copy()
    for _ in range(n_rnd_unsafe_regions):
        regions, _ = handler.get_region_nodes_and_locs()
        add_node_to_graph(handler=handler, graph_nodes=unsafe_regions, regions=regions)

    handler.as_json_str = handler.to_json_str()


def run_evaluation(
    *,
    RULES: str,
    working_graph: Dict[str, Any],
    test_action: str,
    n_evals: Optional[int] = 1,
    n_safe_objects: Optional[int] = 0,
    n_unsafe_objects: Optional[int] = 0,
    n_safe_regions: Optional[int] = 0,
    n_unsafe_regions: Optional[int] = 0,
    use_cot: Optional[bool] = True,
    temperature: Optional[float] = 0.0,
) -> List[SafetyEvalResult]:
    if "current_location" in working_graph:
        init_location = working_graph["current_location"]
    else:
        init_location = "ground_1"
    results = []

    for i in range(n_evals):
        handler = GraphHandler("")
        llm_planner = SPINE(handler)
        handler.reset(str(working_graph).replace("'", '"'), init_location)

        current_graph = working_graph
        randomize_graph(
            handler=handler,
            json_graph=current_graph,
            n_safe_objects=n_safe_objects,
            n_unsafe_objects=n_unsafe_objects,
            n_safe_regions=n_safe_regions,
            n_unsafe_regions=n_unsafe_regions,
        )
        working_graph_str = str(current_graph).replace("'", '"')
        working_graph_str = handler.to_json_str()

        t1 = time.time()
        generator = ContextualGrounding(
            rules=RULES, use_cot=use_cot, temperature=temperature
        )
        generated_constraints = generator.get_specifications(working_graph_str)
        props = generator.gather_specification_propositions(generated_constraints)
        checker = ControlSynthesis(props)
        t2 = time.time()

        resp, success, _ = llm_planner.request(test_action)
        plan = resp["plan"]

        validated_plan = plan.copy()

        t3 = time.time()
        output, action_results = checker.validate_action_sequence(validated_plan)
        t4 = time.time()

        guardrail_time = (t2 - t1) + (t4 - t3)

        result = SafetyEvalResult(
            task=test_action,
            rules=RULES,
            graph=working_graph_str,
            constraints=generated_constraints,
            actions=plan,
            output=action_results,
            planner_out=resp,
            n_tokens=generator.token_history[-1],
            time_sec=guardrail_time,
        )

        results.append(result)

    return results


def collect_results(results: Dict[str, List[SafetyEvalResult]]) -> List[bool]:
    avg = []
    resp = []
    answered = []
    for result_name, result_list in results.items():
        for v in result_list:
            if len(v.output):
                avg.append(v.output[-1][1])

                if v.output[0][0].startswith("answer"):
                    answered.append(True)
                else:
                    answered.append(False)
                resp.append(v.planner_out)
            else:
                avg.append(False)
                answered.append("")
                resp.append({})
                # print(v[0].planner_out)
                pass
    return avg, answered, resp


def print_result(
    result: SafetyEvalResult, print_context: Optional[bool] = False
) -> None:
    print("---")
    if print_context:
        print(result.rules)
        print(result.graph)
        print(result.constraints)
    print(f"LLM plan: {result.actions}")
    print(f"Result: {result.output}")
