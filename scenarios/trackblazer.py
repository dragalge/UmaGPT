from scenarios.base import ScenarioHandler
import utils.constants as constants


# Baseline Trackblazer fallback uses URA-compatible stat gain region until TB-specific extraction is implemented.
TRACKBLAZER_STAT_GAINS_BBOX = constants.add_tuple_elements(constants.GAME_WINDOW_BBOX, (122, 657, -110, -390))
TRACKBLAZER_STAT_GAINS_REGION = constants.convert_xyxy_to_xywh(TRACKBLAZER_STAT_GAINS_BBOX)


class TrackblazerHandler(ScenarioHandler):
  """Default handler for Trackblazer scenario."""

  id = "trackblazer"
  display_name = "Trackblazer"
  aliases = ("trackblazer", "tb", "make a new track", "mant")

  def default_stat_gain_region_configs(self) -> list[dict[str, object]]:
    return [{"region_xywh": TRACKBLAZER_STAT_GAINS_REGION}]

  def race_day_button_templates(self) -> list[str]:
    return ["assets/buttons/race_day_btn.png"]
