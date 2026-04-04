from scenarios.base import ScenarioHandler
from scenarios.ura_finale import URAFinaleHandler
from scenarios.trackblazer import TrackblazerHandler
from scenarios.unity import UnityCupHandler


_handlers_by_id: dict[str, ScenarioHandler] = {}
_active_handler: ScenarioHandler | None = None
_DEFAULT_HANDLER_ID = "ura_finale"


def register_scenario_handler(handler: ScenarioHandler) -> None:
  _handlers_by_id[handler.id] = handler


def initialize_scenario_registry() -> None:
  # Idempotent init to avoid duplicate setup in retries.
  if _DEFAULT_HANDLER_ID not in _handlers_by_id:
    register_scenario_handler(URAFinaleHandler())
    register_scenario_handler(UnityCupHandler())
    register_scenario_handler(TrackblazerHandler())


def get_registered_scenarios() -> dict[str, ScenarioHandler]:
  return dict(_handlers_by_id)


def get_scenario_handler(scenario_name: str | None = None) -> ScenarioHandler:
  initialize_scenario_registry()

  if scenario_name:
    scenario_name = scenario_name.lower()
    for handler in _handlers_by_id.values():
      if handler.matches(scenario_name):
        return handler

  return _handlers_by_id[_DEFAULT_HANDLER_ID]


def set_active_scenario(scenario_name: str | None = None) -> ScenarioHandler:
  global _active_handler
  _active_handler = get_scenario_handler(scenario_name)
  return _active_handler


def get_active_scenario_handler() -> ScenarioHandler:
  global _active_handler
  if _active_handler is None:
    _active_handler = get_scenario_handler(None)
  return _active_handler
