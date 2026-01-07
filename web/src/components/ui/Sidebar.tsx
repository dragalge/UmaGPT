import { cn } from "@/lib/utils"; // Assuming you have a utility for tailwind classes
import { 
  Settings, 
  Dumbbell, 
  Trophy, 
  Layout, 
  Calendar, 
  Star, 
  Zap 
} from "lucide-react"; // Using Lucide icons for a modern feel

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

const navItems = [
  { id: "general", label: "General", icon: Settings },
  { id: "training", label: "Training", icon: Dumbbell },
  { id: "race-style", label: "Race Style", icon: Zap },
  { id: "skills", label: "Skills", icon: Star },
  { id: "schedule", label: "Race Schedule", icon: Calendar },
  { id: "events", label: "Events", icon: Trophy },
  { id: "skeleton", label: "Schedule", icon: Layout },
];

export function Sidebar({ activeTab, setActiveTab, appVersion }: SidebarProps) {
  return (
    <div className="w-64 h-screen sticky top-0 flex flex-col">
      <div className="p-3 py-4 absolute">
        <h1 className="text-3xl font-bold text-primary tracking-tight">Uma Auto Train</h1>
        <span className="text-sm block w-full text-right font-bold text-slate-400 -mt-2">v{appVersion || "Loading..."}</span>
      </div>
      <nav className="flex-1 content-center px-3 space-y-3">
        {navItems.map((item) => (
          <button
            key={item.id}
            onClick={() => setActiveTab(item.id)}
            className={cn(
              "uma-bg w-full flex items-center gap-3 px-3 py-3 rounded-md transition-colors font-medium",
              activeTab === item.id
                ? "bg-primary text-primary-foreground"
                : "text-muted-foreground hover:bg-accent hover:text-accent-foreground cursor-pointer "
            )}
          >
            <item.icon className="w-4 h-4" />
            {item.label}
          </button>
        ))}
      </nav>
    </div>
  );
}