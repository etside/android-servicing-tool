import { AppShell } from "@/components/layout/AppShell";
import { GlassCard } from "@/components/ui/glass-card";

export default function Settings() {
  return (
    <AppShell title="Preferences">
      <div className="mb-6">
        <h2 className="text-2xl font-semibold">Settings</h2>
        <p className="text-sm text-muted-foreground mt-1">Configure eTool behavior, drivers, and appearance.</p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        <GlassCard title="Appearance">
          {["Glass intensity", "Motion reduce", "Show device tooltips"].map((s) => (
            <label key={s} className="flex items-center justify-between py-2.5 text-sm border-b border-white/5 last:border-0">
              <span>{s}</span>
              <input type="checkbox" defaultChecked className="accent-primary w-4 h-4" />
            </label>
          ))}
        </GlassCard>
        <GlassCard title="Drivers">
          {["USB Composite", "Qualcomm 9008", "ADB Interface"].map((s) => (
            <div key={s} className="flex items-center justify-between py-2.5 text-sm border-b border-white/5 last:border-0">
              <span>{s}</span>
              <span className="text-success text-xs">Installed</span>
            </div>
          ))}
        </GlassCard>
        <GlassCard title="About" className="md:col-span-2">
          <p className="text-sm text-muted-foreground">eTool v2.2.0 GUI Upgrade — visionOS Edition</p>
          <p className="text-xs text-muted-foreground mt-2">Web-rebuilt UI inspired by Apple Vision Pro design language.</p>
        </GlassCard>
      </div>
    </AppShell>
  );
}
