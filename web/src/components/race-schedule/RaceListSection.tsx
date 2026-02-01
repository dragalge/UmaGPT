import { ChevronsRight } from "lucide-react";
import RaceSchedule from "./RaceSchedule";
import type { Config, UpdateConfigType } from "@/types";

type Props = {
  config: Config;
  updateConfig: UpdateConfigType;
};

export default function RaceScheduleSection({ config, updateConfig }: Props) {
  const {
    race_schedule,
  } = config;

  return (
    <div className="w-full bg-card p-6 rounded-xl shadow-lg border border-border/20">
      <h2 className="text-3xl font-semibold mb-6 flex items-center gap-3">
        <ChevronsRight className="text-primary" />
        Race Schedule
      </h2>
        <RaceSchedule
          raceSchedule={race_schedule}
          addRaceSchedule={(val) => {
            const updated = (() => {
              const exists = race_schedule.some(
                (r) => r.year === val.year && r.date === val.date
              );

              if (exists) {
                return race_schedule.map((r) =>
                  r.year === val.year && r.date === val.date ? val : r
                );
              }

              return [...race_schedule, val];
            })();

            updateConfig("race_schedule", updated);
          }}
          deleteRaceSchedule={(name, year) =>
            updateConfig(
              "race_schedule",
              race_schedule.filter(
                (race) => race.name !== name || race.year !== year
              )
            )
          }
          clearRaceSchedule={() => updateConfig("race_schedule", [])}
        />
    </div>
  );
}
