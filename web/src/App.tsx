import { useEffect, useState } from "react";

import rawConfig from "../../config.json";
import { useConfigPreset } from "./hooks/useConfigPreset";
import { useConfig } from "./hooks/useConfig";
import { useImportConfig } from "./hooks/useImportConfig";

import type { Config } from "./types";

import { Button } from "./components/ui/button";
import { Input } from "./components/ui/input";
import { Sidebar } from "./components/ui/Sidebar";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue,} from "./components/ui/select";
import { Themes } from "./constants/themes";

import SetUpSection from "./components/set-up/SetUpSection";
import EventSection from "./components/event/EventSection";
import RaceScheduleSection from "./components/race-schedule/RaceScheduleSection";
import SkillSection from "./components/skill/SkillSection";
import RaceStyleSection from "./components/race-style/RaceStyleSection";
import TrainingSection from "./components/training/TrainingSection";
import GeneralSection from "./components/general/GeneralSection";
import Skeleton from "./components/skeleton/Skeleton";

function App() {
  const [appVersion, setAppVersion] = useState<string>("");
  const [activeTab, setActiveTab] = useState<string>("general");

  useEffect(() => {
    fetch("/version.txt", { cache: "no-store" })
      .then(r => {
        if (!r.ok) throw new Error("version fetch failed")
        return r.text()
      })
      .then(v => setAppVersion(v.trim()))
      .catch(() => setAppVersion("unknown"))
  }, []);
  
  const defaultConfig = rawConfig as Config;
  const {activeIndex, activeConfig, presets, setActiveIndex, savePreset, updatePreset} = useConfigPreset();
  const {config, setConfig, saveConfig} = useConfig(activeConfig ?? defaultConfig);
  const { fileInputRef, openFileDialog, handleImport } = useImportConfig({activeIndex, updatePreset, savePreset});

  useEffect(() => {
    if (presets[activeIndex]) {
      setConfig(presets[activeIndex].config ?? defaultConfig);
    } else {
      setConfig(defaultConfig);
    }
  }, [activeIndex, presets, setConfig]);

  const { config_name } = config;
  
  useEffect(() => {
    const selectedTheme = Themes.find((t) => t.id === config.theme) || Themes[0];
    document.documentElement.style.setProperty("--primary", selectedTheme.primary);
    // document.documentElement.style.setProperty("--primary", `var(--${selectedTheme.id}-color)`);
  }, [config.theme]);

  const updateConfig = <K extends keyof typeof config>(key: K, value: (typeof config)[K]) => {
    setConfig((prev) => ({ ...prev, [key]: value }));
  };
          
  const renderContent = () => {
    const props = { config, updateConfig };
    switch (activeTab) {
      case "set-up": return <SetUpSection {...props} />;
      case "general": return <GeneralSection {...props} />;
      case "training": return <TrainingSection {...props} />;
      case "race-style": return <RaceStyleSection {...props} />;
      case "skills": return <SkillSection {...props} />;
      case "schedule": return <RaceScheduleSection {...props} />;
      case "events": return <EventSection {...props} />;
      case "skeleton": return <Skeleton {...props} />;
      default: return <SetUpSection {...props} />;
    }
  };

  return (
    <main className="flex min-h-screen w-full bg-triangles">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} appVersion={appVersion} />
      
      <div className="flex-1 flex flex-col overflow-y-auto">
        <header className="p-6 w-full py-4 self-start border-b border-border flex items-end justify-between sticky top-0 z-10 backdrop-blur-md">
          <div>
            <div className="flex items-center gap-3">
              <div className="space-y-1">
                <label className="text-xs font-thin text-muted-foreground ml-1">Configuration Preset</label>
                <Select value={activeIndex.toString()} onValueChange={(v) => setActiveIndex(parseInt(v))}>
                  <SelectTrigger className="w-auto min-w-[180px] bg-card">
                    <SelectValue placeholder="Select Preset" />
                  </SelectTrigger>
                  <SelectContent>
                    {presets.map((preset, i) => (
                      <SelectItem key={i} value={i.toString()}>
                        {preset.name || `Preset ${i + 1}`} {/* */}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              <div className="space-y-1">
                <label className="text-xs font-thin text-muted-foreground ml-1">Configuration Name</label>
                <Input
                  className="max-w-md min-w-[180px] bg-card border-2 border-primary/20 focus:border-primary/50"
                  placeholder="Preset Name"
                  value={config.config_name}
                  onChange={(e) => updateConfig("config_name", e.target.value)}
                />
              </div>

              <div className="space-y-1">
                <label className="text-xs font-thin text-muted-foreground ml-1">Uma <span className="text-[10px] text-slate-800/40">(Theme)</span></label>
                <Select 
                  value={config.theme || "default"} 
                  onValueChange={(v) => updateConfig("theme" as any, v)}
                >
                  <SelectTrigger className="w-auto bg-card">
                    <SelectValue placeholder="Select Theme" />
                  </SelectTrigger>
                  <SelectContent>
                    {Themes.map((theme) => (
                      <SelectItem key={theme.id} value={theme.id}>
                        <div className="flex items-center gap-2">
                          <div 
                            className="w-3 h-3 rounded-full" 
                            style={{ backgroundColor: theme.primary }} 
                          />
                          {theme.label}
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
 
          </div>

          <div className="flex relative items-end gap-3">
            <p className="text-sm absolute top-[-1rem] end-px align-right text-muted-foreground -mt-2">
              Press <span className="font-bold text-primary">F1</span> to start/stop training.
            </p>
              <Button className="uma-bg ml-3" onClick={openFileDialog} variant="outline" >
                Import
              </Button>
              <input type="file" ref={fileInputRef} onChange={handleImport} className="hidden" />
              <Button className="uma-bg" onClick={() => { savePreset(config); saveConfig(); }}>
                Save Changes
              </Button>
          </div>
        </header>

        <div className="p-6 w-full self-center">
          <div className="animate-in fade-in slide-in-from-bottom-2 duration-300">
            {renderContent()}
          </div>
        </div>
      </div>
    </main>
  );
}

export default App;
