export type Stat = {
  spd: number;
  sta: number;
  pwr: number;
  guts: number;
  wit: number;
};

export type Skill = {
  is_auto_buy_skill: boolean;
  skill_pts_check: number;
  skill_list: string[];
};

export type Config = {
  priority_stat: string[];
  priority_weights: number[];
  skip_training_energy: number;
  never_rest_energy: number;
  skip_infirmary_unless_missing_energy: number;
  priority_weight: string;
  minimum_mood: string;
  minimum_mood_junior_year: string;
  maximum_failure: number;
  prioritize_g1_race: boolean;
  cancel_consecutive_race: boolean;
  stat_caps: Stat;
  skill: Skill;
};
