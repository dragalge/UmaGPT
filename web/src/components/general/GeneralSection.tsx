import { Cog } from "lucide-react";

import type { Config, UpdateConfigType } from "@/types";
import { Input } from "../ui/input";
//import { Checkbox } from "../ui/checkbox";

type Props = {
  config: Config;
  updateConfig: UpdateConfigType;
};

export default function GeneralSection({ config, updateConfig }: Props) {
  const {
    minimum_condition_severity,
  } = config;

  return (
    <div className="w-full bg-card p-6 rounded-xl shadow-lg border border-border/20">
      <h2 className="text-3xl font-semibold mb-6 flex items-center gap-3">
        <Cog className="text-primary" />
        General
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">

        <label>
          <span>Duplicate - To be removed</span>
          <Input
            type="number"
            step={1}
            value={minimum_condition_severity}
            onChange={(e) =>
              updateConfig("minimum_condition_severity", e.target.valueAsNumber)
            }
          />
        </label>
      </div>
    </div>
  );
}
