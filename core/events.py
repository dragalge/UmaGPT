from rapidfuzz import fuzz
import os
import re
import utils.device_action_wrapper as device_action

import core.config as config
import utils.constants as constants
from core.ocr import extract_text
from utils.log import debug, info, warning, error
from utils.screenshot import enhanced_screenshot
from utils.tools import sleep, get_secs

try:
  from weighted_levenshtein import lev, osa, dam_lev
  import numpy as np
  HAS_WEIGHTED_LEVENSHTEIN = True
except ImportError:
  HAS_WEIGHTED_LEVENSHTEIN = False

if HAS_WEIGHTED_LEVENSHTEIN:
  SUB_COSTS = np.ones((128, 128), dtype=np.float64)

  INS_COSTS = np.ones(128, dtype=np.float64)
  DEL_COSTS = np.ones(128, dtype=np.float64)
  # --- DELETION GROUP (Punctuation characters that can be removed when needed) ---
  # Low‑cost deletions for OCR‑prone ASCII symbols (using a simple list)

  deletable_symbols = [
      ';', ':', '.', ',', '-', '_', '(', ')', '[', ']', '/', '\\', '|',
      "'", '"', '`', '~', '%', '@', '#', '$', '*', '+', '=', '<', '>',
      '?', '!', '^', '&'
  ]

  for ch in deletable_symbols:
      DEL_COSTS[ord(ch)] = 0.1

  # --- END DELETION GROUP ---

  # --- VERTICALS GROUP (I-like characters: vertical stroke confusion) ---

  VERTICALS = ['l', 'I', 'i', '|', '!', '1']
  # all vertical characters → '1'
  for a in VERTICALS:
    for b in VERTICALS:
      if a != b:
        SUB_COSTS[ord(a), ord(b)] = 0.15
        SUB_COSTS[ord(b), ord(a)] = 0.15

  # --- END VERTICALS GROUP ---


  # --- ZEROS GROUP (O-like characters: circular confusion) ---
  SUB_COSTS[ord('O'), ord('0')] = 0.15
  SUB_COSTS[ord('0'), ord('O')] = 0.15
  # --- END ZEROS GROUP ---


  # --- S-FIVES GROUP ---
  SUB_COSTS[ord('S'), ord('5')] = 0.2
  SUB_COSTS[ord('5'), ord('S')] = 0.2
  # --- END S-FIVES GROUP ---


  # --- B-EIGHTS GROUP ---
  SUB_COSTS[ord('B'), ord('8')] = 0.2
  SUB_COSTS[ord('8'), ord('B')] = 0.2
  # --- END B-EIGHTS GROUP ---


  # --- Z-TWOS GROUP ---
  SUB_COSTS[ord('Z'), ord('2')] = 0.2
  SUB_COSTS[ord('2'), ord('Z')] = 0.2
  # --- END Z-TWOS GROUP ---


  # --- G-SIXES GROUP ---
  SUB_COSTS[ord('G'), ord('6')] = 0.2
  SUB_COSTS[ord('6'), ord('G')] = 0.2
  # --- END G-SIXES GROUP ---

def event_choice(event_name):
  threshold = 0.8
  choice = 0

  if not event_name:
    return choice

  default_choice = {
    "character_name": "Unknown",
    "event_name": "Unknown Event",
    "chosen": 1
  }

  best_event_name, similarity = find_best_match(event_name, config.EVENT_CHOICES)

  debug(f"Best event name match: {best_event_name}, similarity: {similarity}")

  if similarity >= threshold:
    event = next(
      (e for e in config.EVENT_CHOICES if e["event_name"] == best_event_name),
      None,  # fallback
    )
    debug(
      f"Event found: {event_name} has {similarity * 100:.2f}% similarity with {event['event_name']}"
    )
    debug(f"event name: {event['event_name']}, chosen: {event['chosen']}")
    return event
  else:
    debug(
      f"No event found, {event_name} has {similarity * 100:.2f}% similarity with {best_event_name}"
    )
    return default_choice

def get_event_name():
  img = enhanced_screenshot(constants.EVENT_NAME_REGION)
  text = extract_text(img)
  debug(f"Event name: {text}")
  return text

def find_best_match(text: str, event_list: list[dict]) -> tuple[str, float]:
  """Find the best matching skill and similarity score"""
  if not text or not event_list:
    return "", 0.0

  best_match = ""
  best_similarity = 0.0

  for event in event_list:
    event_name = event["event_name"]
    clean_text = re.sub(
      r"\s*\((?!Year 2\))[^\)]*\)", "", event_name
    ).strip()  # remove parentheses
    clean_text = re.sub(r"[^\x00-\x7F]", "", clean_text)  # remove non-ASCII
    if HAS_WEIGHTED_LEVENSHTEIN:
      dist = lev(
        clean_text,
        text,
        substitute_costs=SUB_COSTS,
        insert_costs=INS_COSTS,
        delete_costs=DEL_COSTS
      )

      max_len = max(len(clean_text), len(text)) or 1
      similarity = 1.0 - (dist / max_len)
    else:
      similarity = fuzz.token_sort_ratio(clean_text, text) / 100
    if similarity > best_similarity:
      best_similarity = similarity
      best_match = event_name

  return best_match, best_similarity

# --- URA duel (Happy Meek) event handling ---

PREDICTION_TEMPLATES = {
  "cross": "assets/ura/prediction_cross.png",
  "triangle": "assets/ura/prediction_triangle.png",
  "circle": "assets/ura/prediction_circle.png",
  "double_circle": "assets/ura/prediction_double_circle.png",
}
# worst to best
PREDICTION_RANKS = ["cross", "triangle", "circle", "double_circle"]
# the hard floor: duels below circle odds are never chosen willingly
GOOD_PREDICTIONS = ["circle", "double_circle"]

# per-career tally of duels taken per stat, so picks spread evenly
# across the priority checkboxes. reset by init_events_py() at career start.
duel_counter = {}

def init_events_py():
  global duel_counter
  duel_counter = {}

DUEL_STAT_KEYWORDS = {
  "speed": "spd",
  "stamina": "sta",
  "power": "pwr",
  "guts": "guts",
  "wits": "wit",
  "wit": "wit",
  "energy": "energy",
}

def read_prediction_marker(event_choices_icon, row_index, choice_vertical_gap=112, retries=0):
  # markers sit at a fixed offset right of the choice icon column, one per row.
  # retries exist because the first frame after the choice icon appears can be
  # mid-animation, before the prediction wedges have rendered.
  x, y = event_choices_icon
  region_xywh = (x + 485, y - 20 + row_index * choice_vertical_gap, 50, 40)
  found = None
  for attempt in range(retries + 1):
    screenshot = device_action.screenshot(region_xywh=region_xywh)
    found = None
    for name in PREDICTION_RANKS:
      path = PREDICTION_TEMPLATES[name]
      if not os.path.isfile(path):
        debug(f"Prediction template missing: {path}, skipping.")
        continue
      # 0.75: correct glyphs validate at 0.90+, the nearest wrong glyph at
      # 0.70, and live frames can carry a small rendering tax.
      matches = device_action.match_template(path, screenshot, threshold=0.75)
      if matches:
        if found is not None:
          warning(f"Duel row {row_index}: multiple prediction markers matched ({found} and {name}), keeping {name}.")
        found = name
    if found is not None:
      break
    if attempt < retries:
      debug(f"Duel row {row_index}: no marker on attempt {attempt + 1}, retrying with a fresh frame.")
      device_action.flush_screenshot_cache()
      sleep(0.4)
  debug(f"Duel row {row_index}: prediction marker: {found}")
  return found

def read_duel_stat(event_choices_icon, row_index, choice_vertical_gap=112):
  x, y = event_choices_icon
  region_xywh = (x + 25, y - 16 + row_index * choice_vertical_gap, 280, 32)
  screenshot = enhanced_screenshot(region_xywh)
  text = extract_text(screenshot).lower()
  debug(f"Duel row {row_index} text: {text}")
  for keyword, stat in DUEL_STAT_KEYWORDS.items():
    if keyword in text:
      return stat
  warning(f"Duel row {row_index}: couldn't parse a stat from '{text}'.")
  return None

def is_duel_event_name(event_name):
  if not event_name:
    return False
  similarity = fuzz.partial_ratio(event_name.lower(), "happy meek's challenge") / 100
  debug(f"Duel event name check: '{event_name}' similarity {similarity:.2f}")
  return similarity >= 0.75

def is_duel_event(event_choices_icon):
  # The event name is the sole gate. It OCRs reliably (observed live as
  # "Happy Meek's Challengel", similarity 1.00 on every real duel, and it
  # correctly rejected every ordinary event that reached it). The old marker
  # fast-path was matching ordinary event artwork against the prediction
  # templates and hijacking normal events, so it was removed.
  return is_duel_event_name(get_event_name())

def select_duel_choice(event_choices_icon, choice_vertical_gap=112):
  x, y = event_choices_icon
  choices = []
  for i in range(3):
    stat = read_duel_stat(event_choices_icon, i)
    marker = read_prediction_marker(event_choices_icon, i, retries=3)
    choices.append({"row": i, "stat": stat, "marker": marker})
  info(f"Duel event detected. Choices: {choices}")

  def rank(choice):
    if choice["marker"] is None:
      return -1
    return PREDICTION_RANKS.index(choice["marker"])

  def times_dueled(choice):
    return duel_counter.get(choice["stat"], 0)

  # hard floor: only circle and double_circle are acceptable odds.
  qualifying = [c for c in choices if c["marker"] in GOOD_PREDICTIONS]

  na_mode = getattr(config, "DUEL_PRIORITY_NA", False)
  priority_stats = getattr(config, "DUEL_PRIORITY_STATS", {})

  candidates = []
  if not na_mode:
    checked = [stat for stat, enabled in priority_stats.items() if enabled]
    candidates = [c for c in qualifying if c["stat"] in checked]

  if not candidates:
    # N/A mode, or no checked stat qualified: fall back to anything at the floor.
    candidates = qualifying

  if candidates:
    # balance first: the stat dueled least this career wins.
    # ties break on better marker, then top row.
    chosen = min(candidates, key=lambda c: (times_dueled(c), -rank(c), c["row"]))
  else:
    # everything is triangle or cross: forced pick, least-bad marker, ties -> top row.
    chosen = min(choices, key=lambda c: (-rank(c), c["row"]))
    warning(f"Duel event: no choice at circle or above, forced least-bad pick.")

  if chosen["stat"] is not None:
    duel_counter[chosen["stat"]] = duel_counter.get(chosen["stat"], 0) + 1

  target = (x, y + chosen["row"] * choice_vertical_gap)
  device_action.click(target=target, text=f"Duel choice: {chosen['stat']} ({chosen['marker']})")
  info(f"Duel event: selected {chosen['stat']} with prediction {chosen['marker']} (row {chosen['row']}). Duel counts this career: {duel_counter}")
  return True

# needs a rework can be more optimized
def select_event():
  event_choices_icon = device_action.locate("assets/icons/event_choice_1.png")
  choice_vertical_gap = 112

  if not event_choices_icon:
    return False

  if constants.SCENARIO_NAME == "ura" and getattr(config, "DUEL_HUNTING_ENABLED", False):
    if is_duel_event(event_choices_icon):
      return select_duel_choice(event_choices_icon)

  if not config.USE_OPTIMAL_EVENT_CHOICE:
    device_action.click(target=event_choices_icon, text=f"Event found, selecting top choice.")
    # click(boxes=event_choices_icon, text="Event found, selecting top choice.")
    return True

  event_name = get_event_name()
  if not event_name or event_name == "":
    debug(f"No event name found, returning False")
    return False
  debug(f"Event Name: {event_name}")

  event = event_choice(event_name)
  chosen = event["chosen"]
  debug(f"Event Choice: {chosen}")
  if chosen == 0:
    device_action.click(target=event_choices_icon, text=f"Event found, selecting top choice.")
    # click(boxes=event_choices_icon, text=f"Event found, selecting top choice.")
    return True

  if event["event_name"] == "A Team at Last":
    debug(f"Team selection event entered")
    current_coords = event_choices_icon
    choice_texts = ["Hoppers", "Runners", "Pudding", "Bloom", "Carrot"]
    test_against = choice_texts[chosen - 1]
    debug(f"test against: {test_against}")
    debug(f"Outside while, coord compare: {current_coords[1]} < {constants.SCREEN_MIDDLE_BBOX[3]}")
    while current_coords[1] < constants.SCREEN_MIDDLE_BBOX[3]:
      debug(f"Coord compare: {current_coords[1]} < {constants.SCREEN_MIDDLE_BBOX[3]}")

      region_xywh = (
        current_coords[0] + 90,
        current_coords[1] - 25,
        500,
        35)
      screenshot = enhanced_screenshot(region_xywh)
      text = extract_text(screenshot)
      debug(f"Text: {text}")
      if test_against == "Carrot":
        debug(f"test against: {test_against} in text: {text}")
        if "Pudding" not in text and "Carrot" in text:
          debug(f"Clicking: {current_coords}")
          device_action.click(target=current_coords, text=f"Selecting optimal choice: {event_name}")
          break
      elif test_against in text:
        debug(f"test against: {test_against} in text: {text}")
        debug(f"Clicking: {current_coords}")
        device_action.click(target=current_coords, text=f"Selecting optimal choice: {event_name}")
        break
      current_coords = (current_coords[0], current_coords[1] + choice_vertical_gap)
  else:
    x = event_choices_icon[0]
    y = event_choices_icon[1] + ((chosen - 1) * choice_vertical_gap)
    # debug(f"Event choices coordinates: {event_choices_icon}")
    debug(f"Event choices coordinates: {event_choices_icon}")
    # debug(f"Clicking: {x}, {y}")
    debug(f"Clicking: {x}, {y}")
    device_action.click(target=(x, y), text=f"Selecting optimal choice: {event_name}")
    # click(boxes=(x, y, 1, 1), text=f"Selecting optimal choice: {event_name}")
    sleep(0.5)
    if "Acupuncturist" in event_name:
      confirm_acupuncturist_y = event_choices_icon[1] + ((4 - 1) * choice_vertical_gap)
      device_action.click(target=(x, confirm_acupuncturist_y), text=f"Selecting optimal choice: {event_name}")
      # click(boxes=(x, confirm_acupuncturist_y, 1, 1), text="Confirm acupuncturist.")
  info(f"Found event: {event_name} || Selected option: {chosen}")
  return True
