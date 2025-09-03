import { Input } from "../ui/input";

type Props = {
  priorityWeights: number[];
  setPriorityWeights: (weight: number, index: number) => void;
};

export default function PriorityWeights({ priorityWeights, setPriorityWeights }: Props) {
  return (
    <div className="flex flex-col gap-4 w-fit px-4">
      <p className="text-xl">Priority Weight Multiplier</p>
      {Array.from({ length: 5 }, (_, i) => (
        <Input type="number" key={i} step={0.05} value={priorityWeights[i]} onChange={(e) => setPriorityWeights(e.target.valueAsNumber, i)} />
      ))}
    </div>
  );
}
