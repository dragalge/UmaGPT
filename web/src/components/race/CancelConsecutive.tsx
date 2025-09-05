import { Checkbox } from "../ui/checkbox";

type Props = {
  cancelConsecutive: boolean;
  setCancelConsecutive: (newState: boolean) => void;
};

export default function CancelConsecutive({ cancelConsecutive, setCancelConsecutive }: Props) {
  return (
    <div className="w-fit">
      <label htmlFor="cancel-consecutive" className="flex gap-2 items-center">
        <span className="text-xl shrink-0">Cancel Consecutive Race?</span>
        <Checkbox id="cancel-consecutive" checked={cancelConsecutive} onCheckedChange={() => setCancelConsecutive(!cancelConsecutive)} />
      </label>
    </div>
  );
}
