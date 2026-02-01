import { Trophy } from "lucide-react";
import IsPositionSelectionEnabled from "./IsPositionSelectionEnabled";
import type { Config, UpdateConfigType } from "@/types";
import { POSITION } from "@/constants";
import { Checkbox } from "../ui/checkbox";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../ui/select";

type Props = {
  config: Config;
  updateConfig: UpdateConfigType;
};

const RANK = ["s", "a", "b", "c", "d", "e", "f", "g"];

export default function RaceStyleSection({ config, updateConfig }: Props) {
  const {
    position_selection_enabled,
    preferred_position,
    enable_positions_by_race,
    positions_by_race,
    minimum_aptitudes: { surface, distance, style },
  } = config;

  return (
    <div className="w-full bg-card p-6 rounded-xl shadow-lg border border-border/20">
      <h2 className="text-3xl font-semibold mb-6 flex items-center gap-3">
        <Trophy className="text-primary" />
        Race Style
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="flex flex-col gap-6">
          <IsPositionSelectionEnabled
            positionSelectionEnabled={position_selection_enabled}
            setPositionSelectionEnabled={(val) =>
              updateConfig("position_selection_enabled", val)
            }
          />
          <div className="flex flex-col gap-2">
            <span className="text-lg font-medium shrink-0">
              Preferred Position
            </span>
            <Select
              disabled={
                !(position_selection_enabled && !enable_positions_by_race)
              }
              value={preferred_position}
              onValueChange={(val) => updateConfig("preferred_position", val)}
            >
              <SelectTrigger className="w-24">
                <SelectValue placeholder="Position" />
              </SelectTrigger>
              <SelectContent>
                {POSITION.map((pos) => (
                  <SelectItem key={pos} value={pos}>
                    {pos.toUpperCase()}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
        <div className="flex flex-col gap-6">
          <label
            htmlFor="position-by-race"
            className="flex gap-2 items-center cursor-pointer"
          >
            <Checkbox
              disabled={!position_selection_enabled}
              id="position-by-race"
              checked={enable_positions_by_race}
              onCheckedChange={() =>
                updateConfig(
                  "enable_positions_by_race",
                  !enable_positions_by_race
                )
              }
            />
            <span className="text-lg font-medium shrink-0">
              Position By Race?
            </span>
          </label>
          <div className="flex flex-col gap-2">
            <p className="text-lg font-medium">Position By Race:</p>
            <div className="flex flex-col gap-2">
              {Object.entries(positions_by_race).map(([key, val]) => (
                <label
                  key={key}
                  htmlFor={key}
                  className="flex gap-2 items-center w-44 justify-between cursor-pointer"
                >
                  <span className="capitalize">{key}</span>
                  <Select
                    disabled={
                      !(enable_positions_by_race && position_selection_enabled)
                    }
                    value={val}
                    onValueChange={(newVal) =>
                      updateConfig("positions_by_race", {
                        ...positions_by_race,
                        [key]: newVal,
                      })
                    }
                  >
                    <SelectTrigger className="w-24">
                      <SelectValue placeholder="Position" />
                    </SelectTrigger>
                    <SelectContent>
                      {POSITION.map((pos) => (
                        <SelectItem key={pos} value={pos}>
                          {pos.toUpperCase()}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </label>
              ))}
            </div>
          </div>
        </div>
        <div className="flex gap-2">Minimum Aptituted
          <div className="flex flex-col gap-2">
            <span className="text-center">surface</span>
            <Select
              value={surface}
              onValueChange={(val) =>
                updateConfig("minimum_aptitudes", {
                  ...config.minimum_aptitudes,
                  surface: val,
                })
              }
            >
            <SelectTrigger>
              <SelectValue placeholder="surface" />
            </SelectTrigger>
            <SelectContent>
              {RANK.map((r) => (
                <SelectItem key={r} value={r}>
                  {r.toUpperCase()}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          </div>
          <div className="border-l"></div>
          <div className="flex flex-col gap-2">
            <span className="text-center">distance</span>
            <Select
              value={distance}
              onValueChange={(val) =>
                updateConfig("minimum_aptitudes", {
                  ...config.minimum_aptitudes,
                  distance: val,
                })
              }
            >
            <SelectTrigger>
              <SelectValue placeholder="distance" />
            </SelectTrigger>
            <SelectContent>
              {RANK.map((r) => (
                <SelectItem key={r} value={r}>
                  {r.toUpperCase()}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          </div>
          <div className="border-l"></div>
          <div className="flex flex-col gap-2">
            <span className="text-center">style</span>
            <Select
              value={style}
              onValueChange={(val) =>
                updateConfig("minimum_aptitudes", {
                  ...config.minimum_aptitudes,
                  style: val,
                })
              }
            >
            <SelectTrigger>
              <SelectValue placeholder="style" />
            </SelectTrigger>
            <SelectContent>
              {RANK.map((r) => (
                <SelectItem key={r} value={r}>
                  {r.toUpperCase()}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          </div>
        </div>
      </div>
    </div>
  );
}
