from typing import Any


class ScenarioHandler:
  """Base scenario contract with safe no-op defaults."""

  id = "base"
  display_name = "Base Scenario"
  aliases = ()

  @classmethod
  def detect_scenario(cls, handlers) -> str | None:
    """Detect active scenario from currently visible screen by probing handlers."""
    for handler in handlers:
      if handler.detect_from_screen():
        return handler.id
    return None

  def matches(self, scenario_name: str) -> bool:
    if not scenario_name:
      return False
    return scenario_name == self.id or scenario_name in self.aliases

  def detect_from_screen(self) -> bool:
    return False

  def on_special_screen(self, context: dict[str, Any] | None = None) -> bool:
    return False

  def on_scenario_detected(self, context: dict[str, Any] | None = None) -> bool:
    """Run one-time scenario initialization work right after detection.

    Return True when the current loop iteration should be short-circuited.
    """
    return False

  def collect_main_state_patch(self, state: dict[str, Any]) -> dict[str, Any]:
    return {}

  def collect_training_state_patch(self, training_data: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    return {}

  def turn_region(self):
    return None

  def year_region(self):
    return None

  def criteria_region(self):
    return None

  def support_card_icon_region(self):
    return None

  def failure_region(self):
    return None

  def energy_region(self):
    return None

  def stat_gain_region_configs(self) -> list[dict[str, Any]]:
    return []

  def default_stat_gain_region_configs(self) -> list[dict[str, Any]]:
    return []

  def race_day_button_templates(self) -> list[str]:
    return ["assets/buttons/race_day_btn.png"]

  def on_turn_read(self, turn_text: str) -> None:
    return

  def consider_item_usage(self, state: dict[str, Any]) -> bool:
    """Optional pre-decision hook to consider using items before train/race choice.

    Return True if the handler consumed the turn flow and the caller should restart.
    """
    return False

  def training_gimmick_score(self, training_name: str, training_data: dict[str, Any], state: dict[str, Any]) -> float:
    return 0.0

  def minimum_training_fixture(self, training_mode: str) -> dict[str, Any]:
    return {}

  def wit_training_energy_bonus(self, training_data: dict[str, Any], state: dict[str, Any]) -> float:
    return 0.0

  def race_day_entry_action(self, options: dict[str, Any] | None = None) -> bool:
    return False

  def enter_race_fallback_action(self, options: dict[str, Any] | None = None) -> bool:
    return False

  def extra_training_log_fields(self, training_data: dict[str, Any]) -> list[tuple[str, Any]]:
    return []
