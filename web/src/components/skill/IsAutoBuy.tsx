import { Checkbox } from "../ui/checkbox";

type Props = {
  isAutoBuySkill: boolean;
  setAutoBuySkill: (value: boolean) => void;
};

export default function IsAutoBuy({ isAutoBuySkill, setAutoBuySkill }: Props) {
  return (
    <label htmlFor="buy-auto-skill" className="flex gap-2 items-center">
      <span className="text-xl shrink-0">Auto Buy Skill? </span>
      <Checkbox id="buy-auto-skill" checked={isAutoBuySkill} onCheckedChange={() => setAutoBuySkill(!isAutoBuySkill)} />
    </label>
  );
}
