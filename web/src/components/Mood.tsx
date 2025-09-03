import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { MOOD } from "@/constants";

type Props = {
  minimumMood: string;
  setMood: (newMood: string) => void;
  minimumMoodJunior: string;
  setMoodJunior: (newMood: string) => void;
};

export default function Mood({ minimumMood, setMood, minimumMoodJunior, setMoodJunior }: Props) {
  return (
    <div className="flex flex-col gap-2 w-fit px-4">
      <p className="text-2xl font-semibold">Mood</p>
      <label htmlFor="mood" className="flex gap-2 items-center">
        <span className="text-xl">Minimum Mood Junior Year</span>
        <Select name="mood" value={minimumMoodJunior} onValueChange={(val) => setMoodJunior(val)}>
          <SelectTrigger className="w-28">
            <SelectValue placeholder="Mood" />
          </SelectTrigger>
          <SelectContent>
            {MOOD.map((m) => (
              <SelectItem key={m} value={m}>
                {m}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </label>
      <label htmlFor="mood" className="flex gap-2 items-center">
        <span className="text-xl">Minimum Mood</span>
        <Select name="mood" value={minimumMood} onValueChange={(val) => setMood(val)}>
          <SelectTrigger className="w-28">
            <SelectValue placeholder="Mood" />
          </SelectTrigger>
          <SelectContent>
            {MOOD.map((m) => (
              <SelectItem key={m} value={m}>
                {m}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </label>
    </div>
  );
}
