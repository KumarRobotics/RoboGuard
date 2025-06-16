from typing import List, Optional, Tuple

from roboguard.generator import ContextualGrounding
from roboguard.prompts.base import BASE_RULES
from roboguard.synthesis import ControlSynthesis


class RoboGuard:
    def __init__(self, rules: Optional[str] = BASE_RULES):
        self.contextual_grounding = ContextualGrounding(rules=rules)
        self.graph = None
        self.contextual_specs = None
        self.synthesizer = None

    def get_rules(self) -> str:
        return self.contextual_grounding.get_rules()

    def get_safety_specs(self) -> List[str]:
        return self.contextual_specs

    def update_context(self, graph: str) -> bool:
        """Update RoboGuard context (ie, semantic graph).

        This will generated new contextual safety specifications.

        Parameters
        ----------
        graph : str
            Semantic graph

        Returns
        -------
        bool
            True if context updated successfully.
        """
        self.graph = graph
        self.contextual_specs = self.contextual_grounding.get_specifications(
            f"Scene Graph: {str(graph)}"
        )
        aggregated_specs = self.contextual_grounding.gather_specification_propositions(
            self.contextual_specs
        )
        self.synthesizer = ControlSynthesis(aggregated_specs)

        return True

    def validate_plan(
        self, plan: List[Tuple[str, str]]
    ) -> Tuple[bool, Tuple[str, bool]]:
        """Validate plan via control synthesis.

        Parameters
        ----------
        plan : List[str]
            Plan as a list of (function, argument).

        Returns
        -------
        Tuple[bool, Tuple[str, bool]]:
        - true if plan is save
        - safety state of each plan in the sequence
        """
        assert (
            self.synthesizer is not None
        ), f"must initialize synthesizer via `update_graph`"
        is_safe, action_results = self.synthesizer.validate_action_sequence(plan)

        return is_safe, action_results
