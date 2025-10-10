export type ChoiceType = {
  id: string;
  event_name: string;
  character_name: string;
  choice_text: string;
  choice_number: string;
  relation: string;
  relation_type: string;
  success_type: string;
  all_outcomes: string;
};

export type CharacterType = {
  id: string;
  name: string;
  rarity: string;
  image_url: string;
};

export type SupportCardType = {
  id: string;
  name: string;
  image_url: string;
  rarity: string;
  type: string;
};

export type EventData = {
  choiceArraySchema: {
    choices: ChoiceType[];
  };
  characterArraySchema: {
    characters: CharacterType[];
  };
  supportCardArraySchema: {
    supportCards: SupportCardType[];
  };
  scenarios: {
    name: string;
    image_url: string;
  }[];
};

export interface EventType {
  character_name: string;
  event_name: string;
  choices: {
    choice_number: string;
    choice_text: string;
    variants: {
      success_type: string;
      all_outcomes: string;
    }[];
  }[];
}

export interface EventChoicesType {
  character_name: string;
  event_name: string;
  chosen: number;
}

export type Event = {
  use_optimal_event_choice: boolean;
  event_choices: EventChoicesType[];
};
