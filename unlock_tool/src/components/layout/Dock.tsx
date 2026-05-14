import { NavLink, useLocation } from "react-router-dom";
import { LayoutDashboard, HardDrive, Activity, SlidersHorizontal } from "lucide-react";
import { cn } from "@/lib/utils";

const dock = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/tools/edl-loader", label: "Flash", icon: HardDrive },
  { to: "/tools/qc-diag", label: "Diagnostics", icon: Activity },
  { to: "/settings", label: "Settings", icon: SlidersHorizontal },
];

export const Dock = () => {
  const { pathname } = useLocation();
  return (
    <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-40 animate-fade-in">
      <div className="glass-strong rounded-full px-3 py-2 flex items-center gap-1">
        {dock.map(({ to, label, icon: Icon }) => {
          const active = pathname === to;
          return (
            <NavLink
              key={to}
              to={to}
              className={cn(
                "flex items-center gap-2 px-4 py-2.5 rounded-full text-sm transition-all",
                active
                  ? "bg-white/10 text-foreground"
                  : "text-muted-foreground hover:text-foreground hover:bg-white/5"
              )}
            >
              <Icon className="w-4 h-4" />
              <span>{label}</span>
            </NavLink>
          );
        })}
      </div>
    </div>
  );
};
