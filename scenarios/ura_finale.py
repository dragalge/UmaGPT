from scenarios.base import ScenarioHandler
import utils.constants as constants
from utils.tools import get_secs, sleep
import utils.device_action_wrapper as device_action
from utils.log import info


URA_STAT_GAINS_BBOX = constants.add_tuple_elements(constants.GAME_WINDOW_BBOX, (122, 657, -110, -390))
URA_STAT_GAINS_REGION = constants.convert_xyxy_to_xywh(URA_STAT_GAINS_BBOX)


class URAFinaleHandler(ScenarioHandler):
  """Default handler for URA Finale scenario."""

  id = "ura_finale"
  display_name = "URA Finale"
  aliases = ("ura", "ura_finale")

  def default_stat_gain_region_configs(self) -> list[dict[str, object]]:
    return [{"region_xywh": URA_STAT_GAINS_REGION}]

  def race_day_button_templates(self) -> list[str]:
    return ["assets/buttons/race_day_btn.png", "assets/ura/ura_race_btn.png"]

  def race_day_entry_action(self, options=None) -> bool:
    if options is None:
      options = {}

    if options.get("year") == "Finale Underway":
      if not device_action.locate_and_click("assets/ura/ura_race_btn.png", min_search_time=get_secs(10), region_ltrb=constants.SCREEN_BOTTOM_BBOX):
        return False
    else:
      if not device_action.locate_and_click("assets/buttons/race_day_btn.png", min_search_time=get_secs(10), region_ltrb=constants.SCREEN_BOTTOM_BBOX):
        return False

    sleep(0.5)
    device_action.locate_and_click("assets/buttons/ok_btn.png")
    sleep(0.5)
    clicked = False
    for _ in range(2):
      for _ in range(5):
        if device_action.locate_and_click("assets/buttons/race_btn.png", min_search_time=get_secs(2)):
          clicked = True
          break
        if device_action.locate_and_click("assets/buttons/bluestacks/race_btn.png", min_search_time=get_secs(2)):
          clicked = True
          break
    if not clicked:
      return False
    sleep(0.5)
    return True

  def enter_race_fallback_action(self, options=None) -> bool:
    if options is None:
      options = {}

    if device_action.locate("assets/buttons/race_day_btn.png", min_search_time=get_secs(2), region_ltrb=constants.SCREEN_BOTTOM_BBOX):
      info("We missed a race day check somehow. Found the race_day_btn now, proceed to race_day.")
      return self.race_day_entry_action(options)

    if device_action.locate("assets/ura/ura_race_btn.png", min_search_time=get_secs(2), region_ltrb=constants.SCREEN_BOTTOM_BBOX):
      info("We missed a race day check somehow. Found the ura_race_btn now, proceed to race_day.")
      return self.race_day_entry_action(options)

    return False
