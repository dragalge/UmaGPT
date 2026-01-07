import { useEffect, useState } from "react";

import rawConfig from "../../config.json";
import { useConfigPreset } from "./hooks/useConfigPreset";
import { useConfig } from "./hooks/useConfig";
import { useImportConfig } from "./hooks/useImportConfig";

import type { Config } from "./types";

import { Button } from "./components/ui/button";
import { Input } from "./components/ui/input";
import { Sidebar } from "./components/ui/Sidebar";

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
  const {
    activeIndex,
    activeConfig,
    presets,
    setActiveIndex,
    savePreset,
    updatePreset,
  } = useConfigPreset();
  const { config, setConfig, saveConfig } = useConfig(
    activeConfig ?? defaultConfig
  );
  const { fileInputRef, openFileDialog, handleImport } = useImportConfig({
    activeIndex,
    updatePreset,
    savePreset,
  });

  useEffect(() => {
    if (presets[activeIndex]) {
      setConfig(presets[activeIndex].config ?? defaultConfig);
    } else {
      setConfig(defaultConfig);
    }
  }, [activeIndex, presets, setConfig]);

  const { config_name } = config;

  const updateConfig = <K extends keyof typeof config>(
    key: K,
    value: (typeof config)[K]
  ) => {
    setConfig((prev) => ({ ...prev, [key]: value }));
  };
          
  const renderContent = () => {
    const props = { config, updateConfig };
    switch (activeTab) {
      case "general": return <GeneralSection {...props} />;
      case "training": return <TrainingSection {...props} />;
      case "race-style": return <RaceStyleSection {...props} />;
      case "skills": return <SkillSection {...props} />;
      case "schedule": return <RaceScheduleSection {...props} />;
      case "events": return <EventSection {...props} />;
      case "skeleton": return <Skeleton {...props} />;
      default: return <GeneralSection {...props} />;
    }
  };

  return (
    <main className="flex min-h-screen w-full bg-triangles">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} appVersion={appVersion} />
      
      <div className="flex-1 overflow-y-auto">
        <header className="p-8 border-b border-border  flex items-center justify-between sticky top-0 z-10 backdrop-blur-md">
          <div>
            <div className="flex gap-2 mt-4">
              {presets.map((_, i) => (
                <Button
                  key={i}
                  variant={i === activeIndex ? "default" : "outline"}
                  size="sm"
                  onClick={() => setActiveIndex(i)}
                >
                  Preset {i + 1}
                </Button>
              ))}
            </div>
            <div className="mt-4">
              <label className="text-sm font-medium text-muted-foreground mb-2 block">Configuration Name</label>
              <Input
                className="max-w-md bg-card border-2 border-primary/20 focus:border-primary/50"
                placeholder="Preset Name"
                value={config.config_name}
                onChange={(e) => updateConfig("config_name", e.target.value)}
              />
            </div>
          </div>

          <div className="flex flex-col items-end gap-3">
            <div className="flex items-center gap-3">
              <Button className="uma-bg" onClick={openFileDialog} variant="outline" >
                Import
              </Button>
              <input type="file" ref={fileInputRef} onChange={handleImport} className="hidden" />
              <Button className="uma-bg" onClick={() => { savePreset(config); saveConfig(); }}>
                Save Changes
              </Button>
            </div>
            <p className="text-sm text-muted-foreground">
              Press <span className="font-bold text-primary">F1</span> to start/stop.
            </p>
          </div>
        </header>

        <div className="max-w-4xl p-8">
          <div className="animate-in fade-in slide-in-from-bottom-2 duration-300">
            {renderContent()}
          </div>
        </div>
      </div>
    </main>
  );
}

export default App;
