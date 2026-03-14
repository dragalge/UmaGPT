import cv2
import re
import utils.constants as constants
import utils.device_action_wrapper as device_action
import core.config as config
from scenarios.base import ScenarioHandler
from core.ocr import extract_allowed_text
from utils.screenshot import enhance_image_for_ocr
from utils.shared import CleanDefaultDict
from utils.log import error, info, warning, debug, debug_window
from utils.tools import get_secs, sleep


UNITY_ENERGY_BBOX = constants.add_tuple_elements(constants.GAME_WINDOW_BBOX, (287, 120, -150, -920))
UNITY_ENERGY_REGION = constants.convert_xyxy_to_xywh(UNITY_ENERGY_BBOX)

UNITY_TURN_BBOX = constants.add_tuple_elements(constants.GAME_WINDOW_BBOX, (110, 60, -630, -975))
UNITY_TURN_REGION = constants.convert_xyxy_to_xywh(UNITY_TURN_BBOX)

UNITY_RACE_TURNS_BBOX = constants.add_tuple_elements(constants.GAME_WINDOW_BBOX, (120, 114, -640, -947))
UNITY_RACE_TURNS_REGION = constants.convert_xyxy_to_xywh(UNITY_RACE_TURNS_BBOX)

UNITY_FAILURE_BBOX = constants.add_tuple_elements(constants.GAME_WINDOW_BBOX, (152, 780, -140, -265))
UNITY_FAILURE_REGION = constants.convert_xyxy_to_xywh(UNITY_FAILURE_BBOX)

UNITY_YEAR_BBOX = constants.add_tuple_elements(constants.GAME_WINDOW_BBOX, (237, 35, -400, -1025))
UNITY_YEAR_REGION = constants.convert_xyxy_to_xywh(UNITY_YEAR_BBOX)

UNITY_CRITERIA_BBOX = constants.add_tuple_elements(constants.GAME_WINDOW_BBOX, (290, 60, -190, -965))
UNITY_CRITERIA_REGION = constants.convert_xyxy_to_xywh(UNITY_CRITERIA_BBOX)

UNITY_STAT_GAINS_2_BBOX = constants.add_tuple_elements(constants.GAME_WINDOW_BBOX, (122, 640, -110, -403))
UNITY_STAT_GAINS_2_REGION = constants.convert_xyxy_to_xywh(UNITY_STAT_GAINS_2_BBOX)

UNITY_STAT_GAINS_BBOX = constants.add_tuple_elements(constants.GAME_WINDOW_BBOX, (122, 673, -110, -378))
UNITY_STAT_GAINS_REGION = constants.convert_xyxy_to_xywh(UNITY_STAT_GAINS_BBOX)

UNITY_SUPPORT_CARD_ICON_BBOX = constants.add_tuple_elements(constants.GAME_WINDOW_BBOX, (665, 130, 0, -380))
UNITY_SUPPORT_CARD_ICON_REGION = constants.convert_xyxy_to_xywh(UNITY_SUPPORT_CARD_ICON_BBOX)

UNITY_TEAM_MATCHUP_BBOX = constants.add_tuple_elements(constants.GAME_WINDOW_BBOX, (130, 565, -130, -475))
UNITY_TEAM_MATCHUP_REGION = constants.convert_xyxy_to_xywh(UNITY_TEAM_MATCHUP_BBOX)


def cache_templates(templates):
  cache = {}
  image_read_color = cv2.IMREAD_COLOR
  for name, path in templates.items():
    img = cv2.imread(path, image_read_color)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    if img is None:
      continue
    cache[name] = img
  return cache


UNITY_SPECIAL_TEMPLATES = {
  "close_btn": "assets/buttons/close_btn.png",
  "unity_cup_btn": "assets/unity/unity_cup_btn.png",
  "unity_banner_mid_screen": "assets/unity/unity_banner_mid_screen.png",
}

CACHED_UNITY_SPECIAL_TEMPLATES = cache_templates(UNITY_SPECIAL_TEMPLATES)

TEAM_MATCHUP_TEMPLATES = {
  "affinity_0": "assets/unity/unity_affinity_0.png",
  "affinity_1": "assets/unity/unity_affinity_1.png",
  "affinity_2": "assets/unity/unity_affinity_2.png",
  "affinity_3": "assets/unity/unity_affinity_3.png",
}

if not hasattr(config, "UNITY_MINIMUM_MATCHUP_SCORE"):
  config.UNITY_MINIMUM_MATCHUP_SCORE = 11

def find_best_match(matchups):
  best_match = matchups[0]
  best_match_score = best_match["score"]
  for matchup in matchups:
    if matchup["score"] > config.UNITY_MINIMUM_MATCHUP_SCORE:
      return matchup
    elif matchup["score"] > best_match_score:
      best_match = matchup
      best_match_score = matchup["score"]
  return best_match

def unity_cup_function():
  tries = 0
  while True:
    device_action.flush_screenshot_cache()
    screenshot = device_action.screenshot()
    select_opponent_btn = device_action.locate("assets/unity/select_opponent_btn.png")
    s_rank_opponent = device_action.locate("assets/unity/s_rank_opponent.png", region_ltrb=constants.SCREEN_MIDDLE_BBOX)
    sleep(0.25)
    if select_opponent_btn:
      break
    elif s_rank_opponent:
      break
    tries += 1
    if tries > 20:
      raise ValueError("Select opponent button not found, please report this.")
  rank_matches = device_action.match_template("assets/unity/team_rank.png", screenshot)
  if not select_opponent_btn and not s_rank_opponent:
    raise ValueError("Select opponent and zenith race button not found, please report this.")
  elif select_opponent_btn:
    select_opponent_mouse_pos = (select_opponent_btn[0], select_opponent_btn[1])
  elif s_rank_opponent:
    sleep(1)
    device_action.click(target=(constants.SKILL_SCROLL_BOTTOM_MOUSE_POS))
    unity_race_start()
    return True
  if len(rank_matches) == 0:
    raise ValueError("Team rank not found, please report this.")
  matchups = []
  # sort matchups by Y coords
  rank_matches.sort(key=lambda x: x[1])
  # for every opponent team
  for rank_match in rank_matches:
    count = CleanDefaultDict()
    x, y, w, h = rank_match
    offset_x = constants.GAME_WINDOW_BBOX[0]
    offset_y = constants.GAME_WINDOW_BBOX[1]
    x = x + offset_x + w // 2
    y = y + offset_y + h // 2
    device_action.click(target=(x, y))
    count["mouse_pos"] = (x, y)
    device_action.click(select_opponent_mouse_pos)
    tries = 0
    while tries < 10:
      if device_action.locate("assets/unity/unity_tazuna.png"):
        break
      tries += 1
      if tries > 10:
        raise ValueError("Affinity screen not found, please report this.")
      device_action.flush_screenshot_cache()
    
    screenshot = device_action.screenshot(region_xywh=UNITY_TEAM_MATCHUP_REGION)
    debug_window(screenshot, save_name="unity_team_matchup")
    
    # find all affinity vs opponent team
    for name, path in TEAM_MATCHUP_TEMPLATES.items():
      matches = device_action.match_template(path, screenshot)
      # if affinity found, count it
      for match in matches:
        count["score"] += int(name.split("_")[1])
        count[name] += 1
    matchups.append(count)
    device_action.locate_and_click("assets/buttons/cancel_btn.png")
    # max of 5 matches, if all is double circle, stop looking at the others since they're the same
    if count["affinity_3"] > 4:
      break
  debug(f"Unity matchups: {matchups}")
  best_match = find_best_match(matchups)
  device_action.click(target=(best_match["mouse_pos"][0], best_match["mouse_pos"][1]))
  device_action.click(select_opponent_mouse_pos)
  unity_race_start()
  return True

def unity_race_start():
  sleep(1)
  device_action.locate_and_click("assets/unity/start_unity_match.png", min_search_time=get_secs(2))
  sleep(1)
  device_action.locate_and_click("assets/unity/see_results.png", min_search_time=get_secs(20), region_ltrb=constants.SCREEN_BOTTOM_BBOX)
  sleep(2)
  device_action.locate_and_click("assets/buttons/skip_btn.png", min_search_time=get_secs(5), region_ltrb=constants.SCREEN_BOTTOM_BBOX)


def collect_unity_training_extras(threshold=0.8):
  extras = CleanDefaultDict()
  screenshot = device_action.screenshot(region_xywh=UNITY_SUPPORT_CARD_ICON_REGION)

  unity_training_matches = device_action.match_template("assets/unity/unity_training.png", screenshot, threshold)
  unity_gauge_matches = device_action.match_template("assets/unity/unity_gauge_unfilled.png", screenshot, threshold)
  unity_spirit_exp_matches = device_action.match_template("assets/unity/unity_spirit_explosion.png", screenshot, threshold)

  for training_match in unity_training_matches:
    extras["unity_trainings"] += 1
    for gauge_match in unity_gauge_matches:
      dist = gauge_match[1] - training_match[1]
      if dist < 100 and dist > 0:
        extras["unity_gauge_fills"] += 1
        # each unity training can only be matched to one gauge fill, so break
        break

  for spirit_exp_match in unity_spirit_exp_matches:
    extras["unity_spirit_explosions"] += 1

  return extras


class UnityCupHandler(ScenarioHandler):
  """Scenario handler for Unity Cup specific interactions."""

  id = "unity"
  display_name = "Unity Cup"
  aliases = ("unity", "unity_cup")

  def turn_region(self):
    return UNITY_TURN_REGION

  def year_region(self):
    return UNITY_YEAR_REGION

  def criteria_region(self):
    return UNITY_CRITERIA_REGION

  def support_card_icon_region(self):
    return UNITY_SUPPORT_CARD_ICON_REGION

  def failure_region(self):
    return UNITY_FAILURE_REGION

  def energy_region(self):
    return UNITY_ENERGY_REGION

  def stat_gain_region_configs(self):
    return [
      {
        "region_xywh": UNITY_STAT_GAINS_REGION,
        "scale_factor": 1.5,
        "secondary_stat_gains": False,
      },
      {
        "region_xywh": UNITY_STAT_GAINS_2_REGION,
        "scale_factor": 1.5,
        "secondary_stat_gains": True,
      },
    ]

  def on_turn_read(self, turn_text: str) -> None:
    race_turns = device_action.screenshot(region_xywh=UNITY_RACE_TURNS_REGION)
    race_turns = enhance_image_for_ocr(race_turns, resize_factor=4, binarize_threshold=None)
    race_turns_text = extract_allowed_text(race_turns, allowlist="0123456789")
    digits_only = re.sub(r"[^\d]", "", race_turns_text)
    if digits_only:
      digits_only = int(digits_only)
      debug(f"Unity cup race turns text: {race_turns_text}")
      if digits_only in [5, 10]:
        debug(f"Race turns left until unity cup: {digits_only}, waiting for 3 seconds to allow banner to pass.")
        sleep(3)

  def collect_training_state_patch(self, training_data, state):
    return collect_unity_training_extras()

  def extra_training_log_fields(self, training_data):
    return [
      ("unity_gauge_fills", training_data["unity_gauge_fills"]),
      ("unity_trainings", training_data["unity_trainings"] - training_data["unity_gauge_fills"]),
      ("unity_spirit_explosions", training_data["unity_spirit_explosions"]),
    ]

  def training_gimmick_score(self, training_name, training_data, state):
    priority_index = 0
    if training_name in config.PRIORITY_STAT:
      priority_index = config.PRIORITY_STAT.index(training_name)
    priority_effect = config.PRIORITY_EFFECTS_LIST[priority_index]
    priority_weight = {
      "HEAVY": 0.75,
      "MEDIUM": 0.5,
      "LIGHT": 0.25,
      "NONE": 0,
    }[config.PRIORITY_WEIGHT]
    priority_adjustment = priority_effect * priority_weight

    year = state["year"].split()[0]
    if year == "Junior":
      year_adjustment = -0.35
    elif year == "Classic":
      year_adjustment = 0
    elif year == "Senior" or year == "Finale":
      year_adjustment = 0.35
    else:
      warning("Didn't get year value, this should not happen.")
      year_adjustment = 0

    score = 0
    if year == "Finale":
      score += (training_data["unity_trainings"] * 0.2 + training_data["unity_gauge_fills"]) * 0.05
    else:
      score += training_data["unity_gauge_fills"] * (1 - year_adjustment)
      score += training_data["unity_trainings"] * 0.1
    if priority_adjustment >= 0:
      score += training_data["unity_spirit_explosions"] * (1 + year_adjustment) * (1 + priority_adjustment)
    else:
      score += training_data["unity_spirit_explosions"] * (1 + year_adjustment) / (1 + abs(priority_adjustment))

    debug(f"Unity training score: {training_name} -> {score}")
    return score

  def minimum_training_fixture(self, training_mode):
    fixtures = {
      "rainbow_training": {"unity_spirit_explosions": 1},
      "max_out_friendships": {"unity_gauge_fills": 1},
      "most_support_cards": {"unity_gauge_fills": 1},
    }
    return fixtures.get(training_mode, {})

  def wit_training_energy_bonus(self, training_data, state):
    return training_data.get("unity_spirit_explosions", 0) * 5

  def detect_from_screen(self) -> bool:
    # Special startup case: when launched from Unity Cup race screen there is no Details button.
    if not device_action.locate_and_click("assets/unity/unity_cup_btn.png", min_search_time=get_secs(1)):
      return False

    debug("Unity race detected from startup screen. Entering Unity Cup flow.")
    unity_cup_function()
    return True

  def on_special_screen(self, context=None) -> bool:
    if context is None:
      context = {}

    click_match = context.get("click_match")

    def _click_match(matches):
      if not matches:
        return False
      if click_match:
        return click_match(matches)
      x, y, w, h = matches[0]
      cx = x + w // 2
      cy = y + h // 2
      return device_action.click(target=(cx, cy), text=f"Clicked match: {matches[0]}")

    if context.get("entry_clicked", False):
      return unity_cup_function()

    unity_matches = device_action.match_cached_templates(CACHED_UNITY_SPECIAL_TEMPLATES, region_ltrb=constants.GAME_WINDOW_BBOX)

    if _click_match(unity_matches.get("unity_cup_btn")):
      debug("Pressed unity cup.")
      return unity_cup_function()

    if _click_match(unity_matches.get("close_btn")):
      debug("Pressed close.")
      return True

    if _click_match(unity_matches.get("unity_banner_mid_screen")):
      debug("Unity banner mid screen found. Starting over.")
      return True

    return False
