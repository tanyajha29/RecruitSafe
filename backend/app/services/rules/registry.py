import os
import json
import logging
from typing import Dict, List, Optional
from app.services.rules.base_rule import BaseRule
from app.services.rules.builtin_rules import RegexPatternRule, PoorGrammarRule, MissingCompanyNameRule

logger = logging.getLogger("recruitsafe")

class RuleRegistry:
    """
    Central registry for managing, loading, and accessing active detection rules.
    Allows dynamic rule addition and modification without code churn.
    """
    def __init__(self):
        self._rules: Dict[str, BaseRule] = {}

    def register(self, rule: BaseRule, overwrite: bool = True) -> None:
        """
        Registers a rule instance in the registry.
        """
        if not isinstance(rule, BaseRule):
            raise TypeError(f"Rule must inherit from BaseRule, got {type(rule)}")

        if rule.rule_id in self._rules and not overwrite:
            logger.warning(f"Rule with ID '{rule.rule_id}' already registered. Skipping.")
            return

        self._rules[rule.rule_id] = rule
        logger.debug(f"Registered rule: '{rule.rule_id}' ({rule.name})")

    def unregister(self, rule_id: str) -> bool:
        """
        Removes a rule from the registry by ID.
        """
        if rule_id in self._rules:
            del self._rules[rule_id]
            logger.debug(f"Unregistered rule: '{rule_id}'")
            return True
        return False

    def get_rule(self, rule_id: str) -> Optional[BaseRule]:
        """
        Retrieves a registered rule by ID.
        """
        return self._rules.get(rule_id)

    def get_all_rules(self) -> List[BaseRule]:
        """
        Returns all currently registered rule instances.
        """
        return list(self._rules.values())

    def get_rules_by_category(self, category: str) -> List[BaseRule]:
        """
        Returns all registered rules under a specific category.
        """
        return [rule for rule in self._rules.values() if rule.category == category]

    def clear(self) -> None:
        """
        Clears all registered rules.
        """
        self._rules.clear()

    def load_from_config(self, config_path: Optional[str] = None) -> int:
        """
        Loads rule definitions from a JSON configuration file.
        Returns the count of rules loaded.
        """
        if not config_path:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            config_path = os.path.join(base_dir, "config", "rules_config.json")

        if not os.path.exists(config_path):
            logger.warning(f"Rule configuration file not found at {config_path}. No JSON rules loaded.")
            return 0

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            loaded_count = 0
            rules_data = data.get("rules", [])
            for item in rules_data:
                rule_obj = RegexPatternRule(
                    rule_id=item["id"],
                    name=item["name"],
                    description=item["description"],
                    category=item["category"],
                    severity=item["severity"],
                    weight_key=item["weight_key"],
                    default_weight=item["default_weight"],
                    keywords=item.get("keywords", []),
                    explanation=item.get("explanation", "")
                )
                self.register(rule_obj, overwrite=True)
                loaded_count += 1

            # Register heuristic/specialized rules
            self.register(PoorGrammarRule(), overwrite=True)
            self.register(MissingCompanyNameRule(), overwrite=True)

            logger.info(f"Successfully loaded and registered {loaded_count + 2} rules into RuleRegistry.")
            return loaded_count
        except Exception as e:
            logger.error(f"Failed to load rule configuration from {config_path}: {e}")
            raise

# Default global registry instance initialized with built-in rules
default_registry = RuleRegistry()
default_registry.load_from_config()
