import re
from inspect import getmembers, isfunction
from typing import List, Tuple

import spot
import spot.jupyter

import roboguard.prompts.api as robot_api

ROBOT_API = [f[0] for f in getmembers(robot_api, isfunction)]


# for printing
spot.setup()


class ControlSynthesis:
    def __init__(self, ltl_props: List[str]):
        """Initialize control synthesis module.

        Parameters
        ----------
        ltl_props : List[str]
            LTL propositions that must hold true.
            This uses the Spot library LTL syntax.
        """
        ltl_formula = self.clean_formula(" & ".join(ltl_props))
        self.automaton = spot.translate(ltl_formula, "Buchi", "complete", "state-based")
        self.bdict = self.automaton.get_dict()
        self.current_pos = None  # proposition tracking current position

    def clean_formula(self, ltl_formula: str) -> str:
        """Clean LTL propositions for model checking.

        Robot API is formatted as `function(argument)`, which conflicts with
        ltl syntax. We change to `function_argument
        """
        functions = ROBOT_API
        pattern = r"\b(" + "|".join(functions) + ")\(([^)]+)\)"
        result = re.sub(pattern, r"\1_\2", ltl_formula)
        return result

    def plt(self) -> spot.jupyter.SVG:
        return self.automaton.show()

    def validate_action_sequence(
        self, actions: List[str]
    ) -> Tuple[bool, List[Tuple[str, bool]]]:
        """Run model checking over LTL constraints. In particular

        1. Generate Buchi Automata from LTL constraints `ltl_props`
        2. Run `actions` through Automata. If we end up at unsafe state
            (non accepting state), we consider the action sequence unsafe.

        Parameters
        ----------
        actions : List[str]
            Actions assumed to be syntactically valid.

        Returns
        -------
        Tuple[bool, List[Tuple[str, bool]]]
            - True if the action sequence is safe
            - Safety result at each step in the action sequence
        """
        actions = self.format_plan_for_checking(actions)
        formatted_actions = [self.clean_formula(action) for action in actions]
        results_info = []
        current_state = self.automaton.get_init_state_number()

        dest_is_accepting = True
        for idx in range(len(formatted_actions)):
            action = formatted_actions[idx]

            action_formula = self.action_to_formula(spot.formula(action))

            # syntax specific logic. Used for location specific
            # proposition logic.
            if action.startswith("goto"):
                self.current_pos = spot.formula(action)

            for edge in self.automaton.out(current_state):
                edge_formula = spot.formula(
                    spot.bdd_format_formula(self.bdict, edge.cond)
                )

                if spot.contains(edge_formula, action_formula):
                    current_state = edge.dst
                    continue

            dest_is_accepting = self.automaton.state_is_accepting(current_state)
            results_info.append((actions[idx], dest_is_accepting))

        return dest_is_accepting, results_info

    def action_to_formula(self, action: spot.formula) -> spot.formula:
        """Generate LTL formula for a given action.

        Note this tracks position history.
        """
        actions = [action]

        # account for position, if the robot hasn't moved
        if self.current_pos is not None and not str(action).startswith("goto"):
            actions.append(self.current_pos)

        formula = []
        ap_set = set(self.automaton.ap())
        for action in actions:
            if action in ap_set:
                formula.append(f"{action}")
                ap_set.remove(action)

        for ap in ap_set:
            formula.append(f"{spot.formula.Not(ap)}")

        current_formula = spot.formula("& ".join(formula))

        return current_formula

    def format_plan_for_checking(self, plan: List[Tuple[str, str]]) -> List[str]:
        """Format plan for model checking via spot.

        Parameters
        ----------
        plan : List[Tuple[str, str]]
            List of (action, argument) tuples

        Returns
        -------
        List[str]
            Format above actions as a single string in the
            `action(argument)` format
        """
        # ignore functions that are not registered
        formatted_plan = []
        for i in range(len(plan)):
            if plan[i][0] in ROBOT_API:
                formatted_plan.append(plan[i])

        # expand plan
        formatted_plan = self.expand_plan(formatted_plan)

        formatted_plan = [f"{function}({arg})" for function, arg in formatted_plan]

        # get into correct formatting
        for i in range(len(formatted_plan)):
            if formatted_plan[i].startswith("inspect"):
                formatted_plan[i] = (
                    formatted_plan[i]
                    .split(",")[0]
                    .replace("((", "(")
                    .replace("'", "")
                    # + ")"
                )
            # TODO we don't consider answer responses
            if formatted_plan[i].startswith("answer"):
                formatted_plan[i] = "answer"  # don't consider specific response

        # append replan
        formatted_plan = (
            formatted_plan
            if not len(formatted_plan) or formatted_plan[-1].startswith("replan")
            else formatted_plan + ["replan"]
        )

        return formatted_plan

    def expand_plan(self, plan: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
        """Expand implied actions.

        For example, `map_region(x)` implies `goto(x), map_region(x)`

        Parameters
        ----------
        plan : List[Tuple[str, str]]

        Returns
        -------
        List[Tuple[str, str]]
        """

        def _contains_goto(plan_list, target_region: str) -> bool:
            if not len(plan_list) or len(plan_list[-1]) != 2:
                return False
            if plan_list[-1][0] != "goto":
                return False
            if plan_list[-1][1] != target_region:
                return False
            return True

        expanded_plan = []
        for action, argument in plan:
            if action == "map_region":
                if not _contains_goto(expanded_plan, argument):
                    expanded_plan.append(("goto", argument))
            expanded_plan.append((action, argument))

        return expanded_plan
