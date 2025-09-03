import { Input } from "../ui/input";

type Props = {
  skillPtsCheck: number;
  setSkillPtsCheck: (value: number) => void;
};

export default function SkillPtsCheck({ skillPtsCheck, setSkillPtsCheck }: Props) {
  return (
    <label className="flex items-center gap-4">
      <span className="text-xl shrink-0">Skill Pts Check</span>
      <Input className="w-24" type="number" min={0} value={skillPtsCheck} onChange={(e) => setSkillPtsCheck(e.target.valueAsNumber)} />
    </label>
  );
}
