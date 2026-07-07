import { EventSchema } from "./event.type";

import { z } from "zod";
import { RaceScheduleSchema } from "./race.type";
import { StatSchema } from "./stat.type";
import { SkillSchema } from "./skill.type";
import { TrainingStrategySchema } from "./training-strategy.type";
import { MinimumAcceptableScoresSchema } from "./game-state.type";
import { FunctionFallbacksSchema } from "./function-fallbacks.type";

export const DuelPriorityStatsSchema = z.object({
  spd: z.boolean(),
  sta: z.boolean(),
  pwr: z.boolean(),
  guts: z.boolean(),
  wit: z.boolean(),
  energy: z.boolean(),
});

// .default() keeps configs exported before the duel feature importable:
// a missing "duel" key validates and silently gains the block, switched off.
export const DuelSchema = z
  .object({
    duel_hunting_enabled: z.boolean(),
    duel_priority_na: z.boolean(),
    duel_priority_stats: DuelPriorityStatsSchema,
  })
  .default({
    duel_hunting_enabled: false,
    duel_priority_na: false,
    duel_priority_stats: {
      spd: false,
      sta: false,
      pwr: false,
      guts: false,
      wit: false,
      energy: false,
    },
  });

export const ConfigSchema = z.object({
  config_name: z.string(),
  theme: z.string().default("Default"),
  priority_stat: z.array(z.string()),
  priority_weights: z.array(z.number()),
  stat_caps: StatSchema,
  sleep_time_multiplier: z.number(),
  skip_training_energy: z.number(),
  never_rest_energy: z.number(),
  skip_infirmary_unless_missing_energy: z.number(),
  hint_hunting_enabled: z.boolean(),
  hint_hunting_weights: StatSchema,
  stop_at_turns: z.array(z.string()),
  use_skip_claw_machine: z.boolean(),
  wit_training_score_ratio_threshold: z.number(),
  rainbow_support_weight_addition: z.number(),
  non_max_support_weight: z.number(),
  scenario_gimmick_weight: z.number(),
  duel: DuelSchema,
  race_turn_threshold: z.number(),
  do_mission_races_if_possible: z.boolean(),
  prioritize_missions_over_g1: z.boolean(),
  minimum_condition_severity: z.number(),
  priority_weight: z.string(),
  minimum_mood: z.string(),
  minimum_mood_junior_year: z.string(),
  // .default() keeps configs exported before the dating feature importable.
  enable_dating: z.boolean().default(false),
  maximum_failure: z.number(),
  minimum_aptitudes: z.object({
    surface: z.string(),
    distance: z.string(),
    style: z.string(),
  }),
  rest_before_summer_energy: z.number(),
  use_adb: z.boolean(),
  device_id: z.string(),
  ocr_use_gpu: z.boolean(),
  notifications_enabled: z.boolean(),
  info_notification: z.string(),
  error_notification: z.string(),
  success_notification: z.string(),
  notification_volume: z.number(),
  use_race_schedule: z.boolean(),
  cancel_consecutive_race: z.boolean(),
  position_selection_enabled: z.boolean(),
  enable_positions_by_race: z.boolean(),
  preferred_position: z.string(),
  positions_by_race: z.object({
    sprint: z.string(),
    mile: z.string(),
    medium: z.string(),
    long: z.string(),
  }),
  race_schedule: z.array(RaceScheduleSchema),
  skill: SkillSchema,
  function_fallbacks: FunctionFallbacksSchema,
  minimum_acceptable_scores: MinimumAcceptableScoresSchema,
  event: EventSchema,
  training_strategy: TrainingStrategySchema,
  window_name: z.string(),
  preset_id: z.string(),
});

export type Config = z.infer<typeof ConfigSchema>;

export type UpdateConfigType = <K extends keyof Config>(
  key: K,
  value: Config[K]
) => void;
