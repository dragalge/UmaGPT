import re
import json

from utils.screenshot import capture_region, enhanced_screenshot
from core.ocr import extract_text, extract_number
from core.recognizer import match_template, count_pixels_of_color

from utils.constants import SUPPORT_CARD_ICON_REGION, MOOD_REGION, TURN_REGION, FAILURE_REGION, YEAR_REGION, MOOD_LIST, CRITERIA_REGION, SKILL_PTS_REGION, ENERGY_REGION

is_bot_running = False

MINIMUM_MOOD = None
PRIORITIZE_G1_RACE = None
IS_AUTO_BUY_SKILL = None
SKILL_PTS_CHECK = None
PRIORITY_STAT = None
MAX_FAILURE = None
STAT_CAPS = None
SKILL_LIST = None
CANCEL_CONSECUTIVE_RACE = None

def load_config():
  with open("config.json", "r", encoding="utf-8") as file:
    return json.load(file)

def reload_config():
  global PRIORITY_STAT, MINIMUM_MOOD, MAX_FAILURE, PRIORITIZE_G1_RACE, CANCEL_CONSECUTIVE_RACE, STAT_CAPS, IS_AUTO_BUY_SKILL, SKILL_PTS_CHECK, SKILL_LIST
  config = load_config()

  PRIORITY_STAT = config["priority_stat"]
  MINIMUM_MOOD = config["minimum_mood"]
  MAX_FAILURE = config["maximum_failure"]
  PRIORITIZE_G1_RACE = config["prioritize_g1_race"]
  CANCEL_CONSECUTIVE_RACE = config["cancel_consecutive_race"]
  STAT_CAPS = config["stat_caps"]
  IS_AUTO_BUY_SKILL = config["skill"]["is_auto_buy_skill"]
  SKILL_PTS_CHECK = config["skill"]["skill_pts_check"]
  SKILL_LIST = config["skill"]["skill_list"]

# Get Stat
def stat_state():
  stat_regions = {
    "spd": (310, 723, 55, 20),
    "sta": (405, 723, 55, 20),
    "pwr": (500, 723, 55, 20),
    "guts": (595, 723, 55, 20),
    "wit": (690, 723, 55, 20)
  }

  result = {}
  for stat, region in stat_regions.items():
    img = enhanced_screenshot(region)
    val = extract_number(img)
    result[stat] = val
  return result

# Check support card in each training
def check_support_card(threshold=0.8):
  SUPPORT_ICONS = {
    "spd": "assets/icons/support_card_type_spd.png",
    "sta": "assets/icons/support_card_type_sta.png",
    "pwr": "assets/icons/support_card_type_pwr.png",
    "guts": "assets/icons/support_card_type_guts.png",
    "wit": "assets/icons/support_card_type_wit.png",
    "friend": "assets/icons/support_card_type_friend.png"
  }

  SUPPORT_FRIEND_LEVELS = {
    "blue": "assets/icons/support_level_blue.png",
    "green": "assets/icons/support_level_green.png",
    "yellow": "assets/icons/support_level_yellow.png",
    "max": "assets/icons/support_level_max.png",
  } ################################################################################ add friendship level as a target at junior level

  count_result = {}

  for key, icon_path in SUPPORT_ICONS.items():
    matches = match_template(icon_path, SUPPORT_CARD_ICON_REGION, threshold)
    count_result[key] = len(matches)

  return count_result

# Get failure chance (idk how to get energy value)
def check_failure():
  failure = enhanced_screenshot(FAILURE_REGION)
  failure_text = extract_text(failure).lower()

  if not failure_text.startswith("failure"):
    return -1

  # SAFE CHECK
  # 1. If there is a %, extract the number before the %
  match_percent = re.search(r"failure\s+(\d{1,3})%", failure_text)
  if match_percent:
    return int(match_percent.group(1))

  # 2. If there is no %, but there is a 9, extract digits before the 9
  match_number = re.search(r"failure\s+(\d+)", failure_text)
  if match_number:
    digits = match_number.group(1)
    idx = digits.find("9")
    if idx > 0:
      num = digits[:idx]
      return int(num) if num.isdigit() else -1
    elif digits.isdigit():
      return int(digits)  # fallback

  return -1

# Check mood
def check_mood():
  mood = capture_region(MOOD_REGION)
  mood_text = extract_text(mood).upper()

  for known_mood in MOOD_LIST:
    if known_mood in mood_text:
      return known_mood

  print(f"[WARNING] Mood not recognized: {mood_text}")
  return "UNKNOWN"

# Check turn
def check_turn():
    turn = enhanced_screenshot(TURN_REGION)
    turn_text = extract_text(turn)

    if "Race Day" in turn_text:
        return "Race Day"

    # sometimes easyocr misreads characters instead of numbers
    cleaned_text = (
        turn_text
        .replace("T", "1")
        .replace("I", "1")
        .replace("O", "0")
        .replace("S", "5")
    )

    digits_only = re.sub(r"[^\d]", "", cleaned_text)

    if digits_only:
      return int(digits_only)
    
    return -1

# Check year
def check_current_year():
  year = enhanced_screenshot(YEAR_REGION)
  text = extract_text(year)
  return text

# Check criteria
def check_criteria():
  img = enhanced_screenshot(CRITERIA_REGION)
  text = extract_text(img)
  return text

def check_skill_pts():
  img = enhanced_screenshot(SKILL_PTS_REGION)
  text = extract_number(img)
  return text

def check_energy_level(threshold=0.85):
  #find where the right side of the bar is on screen
  right_bar_match = match_template("assets/ui/energy_bar_right_end_part.png", ENERGY_REGION, threshold)
  if right_bar_match:
    x, y, w, h = right_bar_match[0]
    energy_bar_length = x

    x, y, w, h = ENERGY_REGION
    top_bottom_middle_pixel = round((y + h) / 2, 0)

    MAX_ENERGY_REGION = (x, top_bottom_middle_pixel, x + energy_bar_length, top_bottom_middle_pixel+1)


    #[118,117,118] is gray for missing energy, region templating for this one is a problem, so we do this
    empty_energy_pixel_count = count_pixels_of_color([118,117,118], MAX_ENERGY_REGION)
    
    #use the energy_bar_length (a few extra pixels from the outside are remaining so we subtract that)
    total_energy_length = energy_bar_length - 1
    hundred_energy_pixel_constant = 236 #counted pixels from one end of the bar to the other, should be fine since we're working in only 1080p
    
    energy_level = ((total_energy_length - empty_energy_pixel_count) / hundred_energy_pixel_constant) * 100
    print(f"Remaining energy guestimate = {energy_level:.2f}")
    return energy_level
  else:
    print(f"Couldn't find energy bar, returning -1")
    return -1