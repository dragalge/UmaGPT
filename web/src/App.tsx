import defaultConfig from "../../config.json";
import { Button } from "./components/ui/button";
import { Input } from "./components/ui/input";
import { Checkbox } from "./components/ui/checkbox";
import { useConfig } from "./hooks/useConfig";
import SkillList from "./components/SkillList";
import PriorityStat from "./components/PriorityStat";
import StatCaps from "./components/StatCaps";
import Mood from "./components/Mood";
import FailChance from "./components/FailChance";
import PrioritizeG1 from "./components/PrioritizeG1";

function App() {
  const { config, setConfig, saveConfig } = useConfig(defaultConfig);

  const { priority_stat, minimum_mood, maximum_failure, prioritize_g1_race, stat_caps, skill } = config;
  const { is_auto_buy_skill, skill_pts_check, skill_list } = skill;

  const setPriorityStat = (newList: string[]) => {
    setConfig((prev) => ({ ...prev, priority_stat: newList }));
  };

  const setMood = (newMood: string) => {
    setConfig((prev) => ({ ...prev, minimum_mood: newMood }));
  };

  const setFail = (newFail: number) => {
    setConfig((prev) => ({ ...prev, maximum_failure: isNaN(newFail) ? 0 : newFail }));
  };

  const setPrioritizeG1 = (newState: boolean) => {
    setConfig((prev) => ({ ...prev, prioritize_g1_race: newState }));
  };

  const setStatCaps = (keys: string, value: number) => {
    setConfig((prev) => ({ ...prev, stat_caps: { ...prev.stat_caps, [keys]: isNaN(value) ? 0 : value } }));
  };

  const setAutoBuySkill = (newState: boolean) => {
    setConfig((prev) => ({ ...prev, skill: { is_auto_buy_skill: newState, skill_pts_check, skill_list } }));
  };

  const setSkillPtsCheck = (newPts: number) => {
    setConfig((prev) => ({ ...prev, skill: { is_auto_buy_skill, skill_pts_check: isNaN(newPts) ? 0 : newPts, skill_list } }));
  };

  const addSkillList = (newList: string) => {
    setConfig((prev) => ({ ...prev, skill: { is_auto_buy_skill, skill_pts_check, skill_list: [newList, ...skill_list] } }));
  };

  const deleteSkillList = (newList: string) => {
    setConfig((prev) => ({ ...prev, skill: { is_auto_buy_skill, skill_pts_check, skill_list: skill_list.filter((s) => s !== newList) } }));
  };

  return (
    <div className="w-full flex justify-center">
      <div className="mt-24 w-3/4">
        <h1 className="text-4xl font-bold">Uma Auto Train</h1>

        <div className="flex flex-col mt-2 gap-4">
          <div className="flex divide-x-2">
            {/* PRIORITY STAT */}
            <PriorityStat priorityStat={priority_stat} setPriorityStat={setPriorityStat} />

            {/* STAT CAPS */}
            <StatCaps statCaps={stat_caps} setStatCaps={setStatCaps} />

            {/* SKILL */}
            <div className="flex flex-col gap-2 w-fit px-4">
              <p className="text-xl">Skill</p>
              <div className="flex flex-col gap-2">
                <label htmlFor="buy-auto-skill" className="flex gap-2 items-center">
                  <span className="text-xl shrink-0">Auto Buy Skill? </span>
                  <Checkbox id="buy-auto-skill" checked={is_auto_buy_skill} onCheckedChange={() => setAutoBuySkill(!is_auto_buy_skill)} />
                </label>
                <label className="flex items-center gap-4">
                  <span className="text-xl shrink-0">Skill Pts Check</span>
                  <Input type="number" min={0} value={skill_pts_check} onChange={(e) => setSkillPtsCheck(e.target.valueAsNumber)} />
                </label>
                <SkillList list={skill_list} addSkillList={addSkillList} deleteSkillList={deleteSkillList} />
              </div>
            </div>
          </div>

          {/* MINIMUM MOOD */}
          <Mood minimumMood={minimum_mood} setMood={setMood} />

          {/* MAX FAIL CHANCE */}
          <FailChance maximumFailure={maximum_failure} setFail={setFail} />

          {/* PRIORITIZE G1 */}
          <PrioritizeG1 prioritizeG1Race={prioritize_g1_race} setPrioritizeG1={setPrioritizeG1} />
        </div>
        <p className="mt-4">
          Press <span className="font-bold">f1</span> to start/stop the bot.
        </p>
        <Button type="button" size={"lg"} className="px-3 py-1 font-semibold text-lg cursor-pointer mt-6" onClick={saveConfig}>
          Save Config
        </Button>
      </div>
    </div>
  );
}

export default App;
