import { NavLink, useLocation } from "react-router-dom";
import { Cpu, Wrench, Smartphone, Terminal, KeyRound, Download, Settings, Plus, Shield } from "lucide-react";
import { cn } from "@/lib/utils";

const items = [
  { to: "/", icon: Cpu, label: "Dashboard" },
  { to: "/tools/edl-loader", icon: Download, label: "EDL Loader" },
  { to: "/tools/adb-enabler", icon: Terminal, label: "ADB Enabler" },
  { to: "/tools/boot-download", icon: Smartphone, label: "Boot → Download" },
  { to: "/tools/keygen", icon: KeyRound, label: "Sierra Keygen" },
  { to: "/tools/qc-diag", icon: Wrench, label: "QC Diag" },
  { to: "/tools/frp-bypass", icon: Shield, label: "FRP Bypass" },
  { to: "/tools/flash", icon: Download, label: "Flash" },
  { to: "/tools/unlock", icon: KeyRound, label: "Unlock" },
  { to: "/tools/activation-removal", icon: Smartphone, label: "Activation Removal" },
  { to: "/tools/passcode-bypass", icon: Terminal, label: "Passcode Bypass" },
  { to: "/settings", icon: Settings, label: "Settings" },
];

export const Sidebar = () => {
  const { pathname } = useLocation();
  return (
    <aside className="fixed left-4 top-1/2 -translate-y-1/2 z-40">
      <nav className="glass-strong rounded-3xl p-3 flex flex-col gap-2 items-center animate-scale-in">
        {items.map(({ to, icon: Icon, label }) => {
          const active = pathname === to;
          return (
            <NavLink
              key={to}
              to={to}
              title={label}
              className={cn(
                "group relative w-12 h-12 rounded-2xl flex items-center justify-center transition-all duration-300",
                active
                  ? "bg-gradient-primary text-primary-foreground glow-primary scale-105"
                  : "text-muted-foreground hover:text-foreground hover:bg-white/5"
              )}
            >
              <Icon className="w-5 h-5" />
              <span className="absolute left-full ml-3 px-3 py-1.5 rounded-xl glass-strong text-xs whitespace-nowrap opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all pointer-events-none">
                {label}
              </span>
            </NavLink>
          );
        })}
        <div className="w-8 h-px bg-border my-1" />
        <button className="w-12 h-12 rounded-2xl flex items-center justify-center text-muted-foreground hover:text-foreground hover:bg-white/5 transition">
          <Plus className="w-5 h-5" />
        </button>
      </nav>
    </aside>
  );
};
