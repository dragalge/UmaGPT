import { REAL_CALENDAR } from "@/constants/race.constant";
import type { Config, UpdateConfigType } from "@/types";
import { Triangle, X } from "lucide-react";
import DialogTimeline from "./Dialog.Timeline";
import { colorFromString } from "@/components/skeleton/ColorFromString";
import { useLayoutEffect, useRef, useState } from "react";

type Props = {
  config: Config;
  updateConfig: UpdateConfigType;
};

export default function Timeline({ config, updateConfig }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [containerWidth, setContainerWidth] = useState(0);

  useLayoutEffect(() => {
    if (!containerRef.current) return;
    const observer = new ResizeObserver((entries) => {
      setContainerWidth(entries[0].contentRect.width);
    });
    observer.observe(containerRef.current);
    return () => observer.disconnect();
  }, []);

  const {
    training_strategy: { timeline: timeline_config },
  } = config;

  // Flatten the calendar into a single array of turns
  const flatCalendar: { year: string; date: string; key: string }[] = [];
  Object.entries(REAL_CALENDAR).forEach(([year, dates]) => {
    dates.forEach((date) => {
      const key = year === "Finale Underway" ? year : `${year} ${date}`;
      flatCalendar.push({ year, date, key });
    });
  });

  // Determine active template for each turn and identify turns where a template starts
  let currentActiveTemplate: string | undefined = undefined;
  const items = flatCalendar.map((item) => {
    const assignedTemplate = timeline_config[item.key];
    if (assignedTemplate) {
      currentActiveTemplate = assignedTemplate;
    }
    return {
      ...item,
      assignedTemplate, // Template explicitly assigned to this date
      activeTemplate: currentActiveTemplate, // Current template (persists until next assignedTemplate)
    };
  });

  const turnWidth = containerWidth / items.length;
  const safeWidth = 160;
  const staggerMap: Record<string, number> = {};
  const lastIndexAtLevel = [-999, -999, -999];

  items.forEach((item, index) => {
    if (item.assignedTemplate) {
      let level = 0;
      while (level < 2 && (index - lastIndexAtLevel[level]) * turnWidth < safeWidth) {
        level++;
      }
      staggerMap[item.key] = level;
      lastIndexAtLevel[level] = index;
    }
  });

  const STAGGER_STYLES = [
    { card: "top-16", line: "h-16" },
    { card: "top-40", line: "h-40" },
    { card: "top-64", line: "h-64" },
  ];

  const maxLevel = Object.values(staggerMap).length > 0 ? Math.max(...Object.values(staggerMap)) : 0;
  const pbClass = ["pb-32", "pb-56", "pb-80"][maxLevel];

  return (
    <div ref={containerRef} className={`w-full overflow-x-visible pt-16 pr-4 ${pbClass}`}>
      <div className="flex min-w-max">
        {items.map((item, index) => {
          const color = colorFromString(item.activeTemplate);
          const isYearStart = index === 0 || items[index - 1].year !== item.year;
          const isYearEnd = index === items.length - 1 || items[index + 1].year !== item.year;
          const zIndex = items.length - index;

          return (
            <div key={item.key} className="flex-1 relative flex flex-col items-stretch group" style={{ zIndex }}>

              {/* Angled Date Label */}
              <div className="absolute -top-2.5 left-1/2 translate-x-[-0.5rem] pointer-events-none w-0 overflow-visible">
                <div className="-rotate-60 whitespace-nowrap text-[10px] capitalize text-slate-500 origin-top-left font-semibold tracking-tighter">
                  {item.date}
                </div>
              </div>

              {/* Timeline Tick Segment */}
              <div
                onDragOver={(e) => {
                  e.preventDefault();
                  e.currentTarget.style.opacity = "0.6";
                }}
                onDragLeave={(e) => {
                  e.currentTarget.style.opacity = "1";
                }}
                onDrop={(e) => {
                  e.preventDefault();
                  e.currentTarget.style.opacity = "1";
                  const templateName = e.dataTransfer.getData("templateName");
                  if (templateName) {
                    updateConfig("training_strategy", {
                      ...config.training_strategy,
                      timeline: {
                        ...config.training_strategy.timeline,
                        [item.key]: templateName,
                      },
                    });
                  }
                }}
                className={`h-10 border-r border-white/40 flex items-center justify-center transition-all hover:opacity-80
                  ${item.year === "Finale Underway" ? "min-w-10" : "left-0"}
                  ${isYearStart ? "rounded-l-full" : ""} 
                  ${isYearEnd ? "rounded-r-full border-r-0" : ""}`}
                style={{
                  backgroundColor: color.backgroundColor,
                  borderColor: color.borderColor,
                }}
              >
                {item.assignedTemplate ? (
                  <div className="w-2 h-2 rounded-full bg-black/40 ring-4 ring-black/5" />
                ) : (
                  <></>
                )}
              </div>

              {/* Year Indicator Header */}
              {isYearStart && (
                <div className={`absolute whitespace-nowrap top-11 flex items-center gap-2 font-bold text-xs uppercase text-muted-foreground tracking-wider ${item.year === "Finale Underway" ? "right-0 flex-row-reverse" : "left-0"}`}>
                  {item.year}
                  {item.year !== "Finale Underway" && (<Triangle size={11} className="rotate-90" />)}
                </div>
              )}

              {/* Connection Line to Card */}
              {item.assignedTemplate && (
                <div
                  className={`absolute top-8 left-1/2 w-px opacity-50 ${STAGGER_STYLES[staggerMap[item.key]].line}`}
                  style={{ backgroundColor: color.borderColor }}
                />
              )}

              {/* Template Card */}
              {item.assignedTemplate && (
                <div className={`absolute left-1/2 -translate-x-1/15 ${STAGGER_STYLES[staggerMap[item.key]].card}`}>
                  <DialogTimeline
                    config={config}
                    updateConfig={updateConfig}
                    year={item.year}
                    date={item.date}
                    value={item.assignedTemplate}
                  >
                    <div className="p-3 border-2 rounded-xl shadow-lg bg-white min-w-[100px] max-w-[160px] text-left text-xs font-semibold break-words hover:shadow-xl hover:scale-105 transition-all cursor-pointer relative group/card"
                      style={{
                        borderColor: color.borderColor,
                        borderLeftWidth: '6px'
                      }}
                    >
                      <div className="text-slate-400 text-[10px] uppercase mb-1 tracking-widest">{item.date}</div>
                      <div className="text-slate-800 leading-tight">
                        {item.assignedTemplate.replaceAll("_", " ")}
                      </div>

                      <div
                        className="absolute -top-2 -right-2 bg-white border shadow-sm rounded-full p-1 opacity-0 group-hover/card:opacity-100 transition-opacity hover:bg-red-50"
                        onClick={(e) => {
                          e.stopPropagation();
                          const newTimeline = { ...config.training_strategy.timeline };
                          delete newTimeline[item.key];
                          updateConfig("training_strategy", {
                            ...config.training_strategy,
                            timeline: newTimeline,
                          });
                        }}
                      >
                        <X size={12} className="text-slate-400 hover:text-red-500" />
                      </div>
                    </div>
                  </DialogTimeline>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
