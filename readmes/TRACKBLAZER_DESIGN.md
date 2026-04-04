[Back to main readme](../README.md)

# Trackblazer Scenario Baseline Design

## Purpose
This document defines the baseline implementation plan for supporting the Trackblazer scenario end-to-end.

Current status:
- Scenario recognition at run start is working.
- Trackblazer scenario module exists but is not implemented yet.

Primary goals for baseline:
1. Collect and persist Trackblazer item/shop state.
2. Adjust race vs training decision logic using hard thresholds.
3. Add item usage decision logic, including high-value combo plays.
4. Modularize scenario handling so new scenarios do not require cross-cutting edits.

---

## Implementation Scope

In scope (baseline):
- Item database and in-run inventory state.
- Shop parsing and purchase planning hooks.
- Race schedule override conditions based on training value.
- Item usage planner with predefined combo rules.
- Scenario modularization and migration of existing logic into per-scenario modules.

Out of scope (later):
- Full auto-tuning of thresholds from telemetry.
- Complex search/planning algorithms beyond heuristic scoring.
- Rare edge case support for every event branch.

---

## Suggested Code Touchpoints

Core files likely involved:
- `scenarios/trackblazer.py`
  - Trackblazer-specific state collection and helper functions.
- `core/state.py`
  - Shared state object extensions (items, shop, currency, combo flags).
- `core/strategies.py`
  - Race override and turn-level action selection changes.
- `core/actions.py`
  - New actions for shop buy/use item (if needed).
- `utils/constants.py`
  - Trackblazer assets, regions, and static thresholds.
- `core/config.py`, `config.template.json`
  - New configuration knobs for thresholds and combo behavior.

New data/config files to add:
- `data/trackblazer_items.json`
  - Item catalog: ID, name, cost, effect type, effect strength, tags.
- Optional: `data/trackblazer_combos.json`
  - Combo definitions and activation windows.

---

## Master Task List

- [x] Milestone 0: Scenario modularization framework (registry + hooks).
- [x] Milestone 0a: Extract URA Finale logic into a dedicated scenario module.
- [x] Milestone 0b: Extract Unity Cup logic into a dedicated scenario module.
- [x] Milestone 1: Item state collection and Trackblazer item database.
- [ ] Milestone 2: Race schedule override by training thresholds.
- [ ] Milestone 3: Item usage and combo move planning.
- [ ] Milestone 4: Tuning and telemetry-based cleanup.

---

## Milestone 0: Scenario Modularization (Required Foundation)

Detailed delivery plan:
- See `readmes/MILESTONE_0_SCENARIO_MODULARIZATION_DELIVERY.md`

### Why This Must Happen First
Scenario-specific behavior is currently distributed across shared modules. This raises regression risk whenever a new scenario is added.

Examples of cross-cutting scenario conditionals today:
- Main loop orchestration and Unity special handling in `core/skeleton.py`.
- Scenario-specific state parsing branches in `core/state.py`.
- Scenario-specific training score bonus in `core/trainings.py`.
- Scenario-specific race-day handling in `core/actions.py`.
- Scenario-specific coordinates and regions in `utils/constants.py`.

### Target Architecture
Introduce a scenario package contract and a registry-based dispatch model.

Proposed package layout:
- `scenarios/base.py`
  - Defines a `ScenarioHandler` interface.
- `scenarios/registry.py`
  - Maps scenario IDs to handlers and exposes resolver utilities.
- `scenarios/ura_finale.py`
  - URA-specific behavior module.
- `scenarios/unity_cup.py`
  - Unity-specific behavior module (migrated from `scenarios/unity.py`).
- `scenarios/trackblazer.py`
  - Trackblazer-specific behavior module.

### Scenario Handler Interface (Proposed)
Each scenario module should implement the same hooks with safe defaults:
- `detect_from_screen() -> bool`
- `collect_main_state_patch(state) -> dict`
- `collect_training_state_patch(training_data, state) -> dict`
- `training_gimmick_score(training_name, training_data, state) -> float`
- `race_day_entry_action(options) -> bool`
- `on_special_screen(context) -> bool`
- `get_regions() -> dict`

This keeps shared flow generic while scenario modules provide differences.

### Concrete Refactor Changes
1. `core/skeleton.py`
  - Replace direct Unity imports/calls with registry + active scenario handler.
  - Route scenario detection and special screen handling through handler hooks.
2. `core/state.py`
  - Remove `if scenario == ...` branches.
  - Let base state collection call scenario patch hooks.
3. `core/trainings.py`
  - Replace hardcoded `unity` gimmick condition with handler callback.
4. `core/actions.py`
  - Route race-day entry button flow through scenario handler instead of URA-specific checks in shared action path.
5. `utils/constants.py`
  - Move scenario-specific regions into scenario modules or dedicated scenario constants files.
6. `utils/log.py`
  - Read extra scenario metrics from optional handler-provided fields instead of hardcoded Unity keys.

### URA Finale and Unity Cup Module Split

#### URA Finale module (`scenarios/ura_finale.py`)
Responsibilities:
- URA-specific race-day button behavior.
- URA-specific race transition quirks.
- Any URA-specific region overrides.

Migration notes:
- Move URA race button assumptions out of shared race flow.
- Keep URA as the default fallback handler for backwards compatibility.

#### Unity Cup module (`scenarios/unity_cup.py`)
Responsibilities:
- Unity cup event loop interactions currently coupled to main skeleton loop.
- Unity training extra state extraction and gimmick score logic.
- Unity-specific region/asset references.

Migration notes:
- Move `unity_cup_function` and related special screen logic behind `on_special_screen` hook.
- Move Unity training extras and score logic behind scenario patch/gimmick hooks.

### Migration Plan
1. Add base handler + registry with default no-op behavior.
2. Implement `ura_finale` handler and wire as default.
3. Implement `unity_cup` handler using existing behavior.
4. Replace shared scenario conditionals incrementally in skeleton/state/trainings/actions.
5. Add Trackblazer handler on top of modular framework.
6. Remove old branch logic after parity tests pass.

### Acceptance Criteria
- Adding a new scenario only requires:
  - New scenario module registration.
  - New assets/data files.
  - No edits in shared decision flow modules for scenario-specific logic.
- URA and Unity behavior remains functionally equivalent after extraction.
- No direct scenario-name string branching remains in shared core flow (except detection/registry resolution boundary).

---

## Milestone 1: Item State Collection and Item Database

### Requirements
- Build a Trackblazer item catalog containing:
  - Item ID
  - Item name
  - Shop cost
  - Effect metadata (stats, duration, conditions, stack behavior)
  - Tags (`training_boost`, `summer_peak`, `energy`, `race_support`, etc.)
- Collect current run item state each turn:
  - Owned items (counts)
  - Current shop offerings
  - Available currency/resource for purchases

### Proposed State Shape
Add fields to the run state object:
- `scenario_name`: already available
- `trackblazer`:
  - `currency`: int
  - `inventory`: map[item_id -> count]
  - `shop_offers`: list of `{ item_id, cost, stock, detected_name }`
  - `active_item_effects`: list of active buffs/effects
  - `last_shop_scan_turn`: string

### Tasks
1. Create and maintain `data/trackblazer_items.json`.
2. Implement Trackblazer OCR/template detection routines in `scenarios/trackblazer.py`.
3. Hook Trackblazer state collection into main flow when scenario is Trackblazer.
4. Add validation and fallback for unknown items:
  - Store unresolved entries in logs for manual mapping.
5. Add debug logging for each shop/inventory parse.

### Acceptance Criteria
- On every Trackblazer turn, state includes valid inventory + currency data.
- Unknown/ambiguous item detections are safely logged without crashing.
- Item catalog lookups are deterministic by item ID.

---

## Milestone 2: Race Schedule Override by Training Thresholds

### Problem
Current race schedule logic can force races even when training value is exceptionally high. Trackblazer adds stronger training spike potential, so race decisions must be overrideable.

### Baseline Rule Set
Use hard-coded thresholds to skip scheduled race when training opportunity is strong enough.

Candidate baseline checks:
- `total_stat_gain >= X` where X is phase-based.
- `weighted_training_score - race_value_score >= Y`.
- Optional stat-specific gates:
  - If speed/power gain exceeds configured thresholds, prefer training.

Suggested threshold config structure:
- `TRACKBLAZER_RACE_OVERRIDE_ENABLED`
- `TRACKBLAZER_RACE_OVERRIDE_BY_PHASE`
  - `Junior Year`: `{ min_total_stat_gain, min_score_delta }`
  - `Classic Year`: `{ ... }`
  - `Senior Year`: `{ ... }`

### Tasks
1. Add config values to `config.template.json` and wire to `core/config.py`.
2. Compute race opportunity score and training opportunity score in strategy decision path.
3. Modify scheduled race handling in `core/strategies.py`:
  - Evaluate race override before locking `do_race`.
4. Add debug logs showing why race is kept or skipped.

### Acceptance Criteria
- Scheduled race is skipped when configured threshold conditions are met.
- Decision reason is visible in logs with raw threshold values.
- Behavior is stable when config is disabled (no regression).

---

## Milestone 3: Item Usage and Combo Move Planning

### Problem
Some item combinations produce significantly more value when used together in specific windows (example: megaphones + ankle weights during summer training).

### Baseline Design
Add a combo-aware planner that evaluates item usage candidates each turn.

Planner responsibilities:
- Detect if current turn is inside a high-value window (summer camp, key training blocks, etc.).
- Evaluate single-item and combo-item plays.
- Compare "use now" vs "hold for combo" expected value.

### Combo Data Model
Each combo definition should include:
- `combo_id`
- `items_required` (item IDs and counts)
- `time_window` (for example `summer_only`)
- `min_training_value` threshold
- `expected_multiplier` or additive score bonus
- `priority`

### Decision Flow
1. Build candidate plays:
  - No item
  - Single item uses
  - Valid combos from inventory
2. Score each play using current training options and timing context.
3. Select best play above a minimum confidence threshold.
4. Execute item action before training/race action when required.

### Tasks
1. Add combo definitions (`data/trackblazer_combos.json` or constants).
2. Implement combo eligibility + scoring helper in Trackblazer logic module.
3. Add item-use action integration in decision sequence.
4. Add safety limits:
  - Max items used per turn.
  - Prevent consuming long-horizon combo pieces too early unless score is high.

### Acceptance Criteria
- Bot can detect and execute at least one predefined high-value combo reliably.
- Bot avoids burning combo items outside defined windows unless justified by score.
- Logs show selected combo and expected reason/score.

---

## Instrumentation and Validation

Recommended logging and checks:
- Per-turn snapshot for Trackblazer state (`currency`, `inventory`, top shop offers).
- Decision trace for race override and combo planner:
  - Input scores
  - Chosen action
  - Rejected alternatives (brief reason)

Recommended test coverage:
- Unit tests for item catalog parsing and lookup.
- Unit tests for race override threshold function.
- Unit tests for combo eligibility/scoring helpers.
- At least one integration test path for Trackblazer turn decision.

---

## Delivery Order

1. Milestone 0 (scenario modularization)
2. Milestone 1 (state + item catalog)
3. Milestone 2 (race override)
4. Milestone 3 (item combo usage)
5. Tuning pass based on logs

This order reduces risk because Trackblazer feature work will otherwise keep adding scenario branches in shared logic. Modularization first isolates behavior and lowers regression risk for URA and Unity.

---

## Future Considerations

Likely follow-up areas after baseline:
- Better OCR/template robustness for similar-looking item icons.
- Dynamic threshold tuning from historical run outcomes.
- Scenario-specific strategy templates for different training goals.
- More advanced planning that models multi-turn item opportunity cost.
- Tooling to auto-generate or verify item database updates.

Keep this document updated as Trackblazer support expands.
