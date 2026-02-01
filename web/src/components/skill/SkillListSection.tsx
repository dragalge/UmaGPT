import { BrainCircuit } from "lucide-react";
import SkillList from "./SkillList";
import type { Config, UpdateConfigType } from "@/types";

type Props = {
  config: Config;
  updateConfig: UpdateConfigType;
};

export default function SkillSection({ config, updateConfig }: Props) {
  const { skill } = config;

  return (
    <div className="w-full h-full bg-card p-6 rounded-xl shadow-lg border border-border/20">
      <h2 className="text-3xl font-semibold mb-6 flex items-center gap-3">
        <BrainCircuit className="text-primary" />
        Skill List
      </h2>

        <SkillList
          list={skill.skill_list}
          addSkillList={(val) =>
            updateConfig("skill", {
              ...skill,
              skill_list: [val, ...skill.skill_list],
            })
          }
          deleteSkillList={(val) =>
            updateConfig("skill", {
              ...skill,
              skill_list: skill.skill_list.filter((s) => s !== val),
            })
          }
        />

    </div>
  );
}
