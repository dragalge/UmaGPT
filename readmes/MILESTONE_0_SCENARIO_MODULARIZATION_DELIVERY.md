# Milestone 0 Delivery Doc: Scenario Modularization

[Back to main readme](../README.md)

## Objective

Modularize scenario-specific behavior behind a scenario handler contract so new scenarios can be added without scattered edits across shared core modules.

This milestone is a prerequisite for stable Trackblazer implementation.

## Terminology Clarification

- URA Finale: the scenario.
- URA Finals: the end-race sequence inside URA Finale (and also appears in other career contexts).

This doc uses URA Finale when referring to scenario-level module ownership and URA Finals when referring to the end-race flow.

---

## Current Coupling Snapshot (Codebase Findings)

Scenario logic is currently mixed into shared flow at multiple layers:

1. Main loop and special screen handling:

   - `core/skeleton.py`
   - Direct Unity import and calls in the main loop (`unity_cup_function`).
   - Scenario detection and active scenario state are controlled globally (`constants.SCENARIO_NAME`).

2. Shared state collection:

   - `core/state.py`
   - Multiple `if constants.SCENARIO_NAME == "unity"` branches for regions and parsing logic.
   - URA-specific stat-gain and race button checks are in shared state functions.

   . Shared training scoring:

   - `core/trainings.py`
   - Scenario gimmick score and Unity-specific training factors are hardcoded in shared score functions.

3. Shared action execution:

   - `core/actions.py`
   - Race day and enter-race paths include URA button assumptions in generic action methods.

4. Shared constants and logging:

   - `utils/constants.py`
   - Scenario-specific regions are globally defined in a shared constants file.
   - `utils/log.py` has hardcoded Unity extra metrics.

5. Scenario package state:

   - `scenarios/unity.py` contains substantial Unity-specific logic.
   - `scenarios/trackblazer.py` exists but is currently empty.

---

## Target Architecture

### Scenario Contract

Create a standard scenario handler interface with safe defaults.

Proposed hooks:

- `id` and `display_name`
- `detect_from_screen() -> bool`
- `on_special_screen(context) -> bool`
- `collect_main_state_patch(state) -> dict`
- `collect_training_state_patch(training_data, state) -> dict`
- `training_gimmick_score(training_name, training_data, state) -> float`
- `race_day_entry_action(options) -> bool`
- `enter_race_fallback_action(options) -> bool`
- `extra_training_log_fields(training_data) -> list[tuple[str, str | int | float]]`

### Package Layout

- `scenarios/base.py`
  - Base handler class (no-op defaults).
- `scenarios/registry.py`
  - Scenario registration + active scenario resolver.
- `scenarios/ura_finale.py`
  - URA Finale scenario handler.
- `scenarios/unity.py`
  - Unity Cup scenario handler.
- `scenarios/trackblazer.py`
  - Trackblazer handler.

---

## Where To Start Modularizing (Recommended Sequence)

### Start Point A: Build Registry and Default Handler

Reason:

- Lowest-risk change with high leverage.
- Lets shared modules switch to handler calls incrementally.

First edits:

1. Add `scenarios/base.py` and `scenarios/registry.py`.
2. In `core/skeleton.py`, replace direct Unity import with registry lookups.
3. Keep existing behavior by wiring URA Finale handler as default fallback.

### Start Point B: Isolate Unity Special-Screen Flow

Reason:

- Unity has the highest visible branching in the orchestration loop.

First edits:

1. Move/copy `scenarios/unity.py` logic into `scenarios/unity.py`.
2. Replace in-loop Unity checks in `core/skeleton.py` with `active_handler.on_special_screen(...)`.
3. Keep function parity before any behavior changes.

### Start Point C: Split State Parsing by Handler Hooks

Reason:

- `core/state.py` has repeated scenario branches and is the best place to eliminate global conditionals.

First edits:

1. Keep generic base collection in `core/state.py`.
2. Route scenario deltas through `collect_main_state_patch` and `collect_training_state_patch`.
3. Move Unity region overrides and extraction logic to Unity handler.

### Start Point D: Split Training Gimmick Scoring

Reason:

- Prevents future scenario score logic from touching shared scoring code.

First edits:

1. Replace `add_scenario_gimmick_score` hardcoded Unity branch in `core/trainings.py`.
2. Call `active_handler.training_gimmick_score(...)` and merge score in shared path.

### Start Point E: Split Race-Day / Race Entry Overrides

Reason:

- Clarifies URA Finale scenario behavior vs URA Finals race sequence behavior.

First edits:

1. In `core/actions.py`, route URA-specific race-day/enter-race special cases through handler hooks.
2. Keep generic race flow in shared actions.

---

## Delivery Plan (Milestone 0)

### Phase 0: Scaffolding

Deliverables:

- `scenarios/base.py`
- `scenarios/registry.py`
- Active handler lifecycle in core loop.

Definition of done:

- Bot still runs URA Finale baseline with no behavior change.

### Phase 1: Unity Cup Extraction

Deliverables:

- `scenarios/unity.py` with special-screen handling and matchup race logic.
- `core/skeleton.py` delegates Unity-specific loop handling to active handler.

Definition of done:

- Unity Cup branch behavior remains equivalent to current implementation.

### Phase 2: State Hook Migration

Deliverables:

- Scenario hook calls in `core/state.py`.
- Unity state extraction moved from shared branches to handler patch logic.

Definition of done:

- Shared state collection no longer has direct Unity branching in migrated sections.

### Phase 3: Training Gimmick Hook Migration

Deliverables:

- Shared training score pipeline calls handler-provided gimmick score.
- Unity-specific score code moved out of core shared path.

Definition of done:

- Unity score behavior unchanged under tests/log comparison.

### Phase 4: Race-Day Hook Migration

Deliverables:

- Shared actions call scenario race-day and fallback hooks.
- URA Finale module owns URA-specific race button handling.

Definition of done:

- URA race-day path works as before.
- No URA-only behavior remains hardcoded in generic action path.

### Phase 5: Constants and Logging Decoupling

Deliverables:

- Scenario-specific regions moved to scenario modules or per-scenario constants modules.
- Logging reads handler extra fields instead of hardcoded Unity field lists.

Definition of done:

- Shared constants/logging are scenario-agnostic.

---

## URA Finale and Unity Cup Module Ownership

### URA Finale (`scenarios/ura_finale.py`)

Owns:

- Scenario detection hinting/fallback.
- URA Finale race-day entry differences.
- Any URA Finale-specific region overrides.

Does not own:

- Generic race scrolling/selection flow.
- Shared stat/training score framework.

### Unity Cup (`scenarios/unity.py`)

Owns:

- Unity Cup special-screen handling and matchup selection.
- Unity-specific training extras (gauge/spirit/training counters).
- Unity-specific gimmick scoring contribution.

Does not own:

- Generic turn loop and shared action sequencing.

---

## Risks and Mitigations

1. Behavior regressions during extraction.

   - Mitigation: one subsystem at a time with parity logs.

2. Hidden coupling through global `constants.SCENARIO_NAME`.

   - Mitigation: keep global read compatibility during migration, but source active handler from registry.

3. Incomplete ownership boundaries.

   - Mitigation: enforce checklist for each moved concern (orchestration, state, scoring, actions, logging).

---

## Validation Strategy

1. URA Finale regression run (multiple turns):

   - Confirm state collection, race-day, and training paths unchanged.

2. Unity Cup regression run:

   - Confirm special-screen handling and matchup flow unchanged.

3. Log parity checks:

   - Compare action decisions and scenario-specific score components before/after migration.

4. Code review gate:

   - No new scenario conditionals in shared core modules for migrated concerns.

---

## Milestone 0 Exit Criteria

Milestone 0 is complete when all are true:

1. URA Finale and Unity Cup each have dedicated scenario modules with clear ownership.
2. Shared core modules call scenario hooks instead of hardcoded scenario branches for migrated concerns.
3. Adding a new scenario requires registration + module implementation only.
4. URA Finale and Unity Cup behavior is verified equivalent by targeted regression runs.

---

## Current Implementation Status (Updated: 2026-03-13)

This section reflects code changes completed so far.

### Phase 0: Scaffolding

Status: Done

- `scenarios/base.py` and `scenarios/registry.py` are in place.
- Active handler lifecycle is wired in `core/skeleton.py`.
- Default handler fallback is `URA Finale`.

### Phase 1: Unity Cup Extraction

Status: Done (implementation)

- Unity special-screen and matchup flow are handled by `scenarios/unity.py`.
- `core/skeleton.py` delegates special-screen handling to active scenario handler hooks.

### Phase 2: State Hook Migration

Status: Done (implementation)

- `core/state.py` routes through scenario hooks.
- Unity state-specific regions and extraction are owned by `scenarios/unity.py`.
- Shared state no longer branches on scenario for migrated concerns.

### Phase 3: Training Gimmick Hook Migration

Status: Done (implementation)

- Shared training score flow now uses `training_gimmick_score(...)` hook.
- Unity gimmick scoring logic lives in `scenarios/unity.py`.
- Shared minimum-threshold fixtures and wit energy bonus are handler-driven.

### Phase 4: Race-Day Hook Migration

Status: Done (implementation)

- Shared actions call `race_day_entry_action(...)` and `enter_race_fallback_action(...)` hooks.
- URA-specific race-day behavior is owned by `scenarios/ura_finale.py`.

### Phase 5: Constants and Logging Decoupling

Status: Done (implementation)

- Logging uses handler-provided extra fields instead of hardcoded Unity fields.
- Scenario-specific region ownership moved into scenario modules.
- Shared `utils/constants.py` no longer defines Unity/URA scenario regions used by migrated paths.

### Current Practical Notes

- Trackblazer remains baseline scaffolding only (intentional for now).
- Regression/parity tests are intentionally deferred to a later pass.
- Milestone is considered code-complete pending deferred validation.

---

## Deferred Validation Checklist (Run Later)

Use this checklist when returning to full validation.

- [ ] URA Finale regression run across multiple turns (state read, race day, training loop).
- [ ] Unity Cup regression run for special-screen flow and matchup selection.
- [ ] Verify per-training Unity extras are correctly attributed in logs and action decisions.
- [ ] Compare before/after action choice parity for representative URA and Unity saves.
- [ ] Confirm no new scenario conditionals were introduced in shared `core/*` migrated paths.
- [ ] Confirm adding a new scenario still requires only registration + scenario module implementation.
- [ ] Reconfirm bot startup scenario detection is stable from non-standard entry screens.
- [ ] Close Milestone 0 formally after parity confidence is acceptable.

---

## Immediate Next PR Slice (Recommended)

Scope a minimal first PR to reduce risk:

1. Add `scenarios/base.py` and `scenarios/registry.py`.
2. Add `scenarios/ura_finale.py` as default no-op-compatible handler.
3. Wire active scenario handler initialization in `core/skeleton.py` without changing behavior logic yet.
4. Add lightweight logs showing selected scenario handler per run.

This creates the migration backbone with minimal functional change.

[Back to main readme](../README.md)
