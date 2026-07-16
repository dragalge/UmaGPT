import { CALENDAR, CALENDAR_JUNIOR } from "@/constants/race.constant";
import type { RaceScheduleType, RaceType } from "@/types/race.type";
import RaceDateCard from "./RaceDateCard";

type Props = {
  races: Record<string, RaceType>;
  year: string;
  raceSchedule: RaceScheduleType[];
  addRaceSchedule: (race: RaceScheduleType) => void;
  deleteRaceSchedule: (name: string, year: string) => void;
};

export default function RaceCalendar({
  races,
  year,
  raceSchedule,
  addRaceSchedule,
  deleteRaceSchedule,
}: Props) {
  const dates = year === "Junior Year" ? CALENDAR_JUNIOR : CALENDAR;

  return (
    <>
      {dates.map((date) => (
        <RaceDateCard
          key={date}
          date={date}
          year={year}
          races={races}
          raceSchedule={raceSchedule}
          addRaceSchedule={addRaceSchedule}
          deleteRaceSchedule={deleteRaceSchedule}
        />
      ))}
    </>
  );
}