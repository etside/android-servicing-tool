import { AppShell } from "@/components/layout/AppShell";
import { GlassCard } from "@/components/ui/glass-card";
import {
  Smartphone, Cpu, HardDrive, Wifi, Battery, CheckCircle2, XCircle,
  ArrowUpRight, Activity, Zap, Shield, Download, KeyRound, Terminal,
} from "lucide-react";
import { NavLink } from "react-router-dom";
import { useApi } from "@/hooks/useApi";

interface DeviceEntry {
  serial?: string;
  mode?: string;
  state?: string;
  vendor_id?: string;
  product_id?: string;
  manufacturer?: string;
  product?: string;
}

interface DevicesResponse {
  adb: DeviceEntry[];
  fastboot: DeviceEntry[];
  usb: DeviceEntry[];
  ios: DeviceEntry[];
}

const MODE_COLOR: Record<string, string> = {
  adb: "text-green-400",
  recovery: "text-yellow-400",
  fastboot: "text-orange-400",
  qualcomm_edl: "text-red-400",
  mediatek_brom: "text-red-400",
  mediatek_preloader: "text-red-400",
  samsung_download: "text-red-400",
  charging: "text-slate-400",
  mtp: "text-slate-400",
  ptp: "text-slate-400",
  unauthorized: "text-yellow-400",
  ios_normal: "text-green-400",
  ios_recovery: "text-yellow-400",
  ios_dfu: "text-red-400",
};

function ModeBadge({ mode }: { mode?: string }) {
  const m = mode ?? "unknown";
  const color = MODE_COLOR[m] ?? "text-primary";
  return (
    <span className={`text-xs font-mono font-semibold uppercase ${color}`}>{m}</span>
  );
}

function DeviceRow({ d, platform }: { d: DeviceEntry; platform: string }) {
  const label =
    platform === "ios"
      ? `Apple iOS · ${d.product ?? ""}`
      : d.manufacturer
      ? `${d.manufacturer} ${d.product ?? ""}`.trim()
      : d.serial ?? d.vendor_id ?? "Unknown";
  return (
    <div className="flex items-center justify-between p-2.5 rounded-xl bg-white/[0.03] hover:bg-white/[0.06] transition text-sm">
      <div className="flex items-center gap-2">
        <Smartphone className="w-4 h-4 text-muted-foreground shrink-0" />
        <span className="truncate max-w-[160px]">{label}</span>
        {d.serial && (
          <span className="text-xs text-muted-foreground font-mono">{d.serial}</span>
        )}
      </div>
      <ModeBadge mode={d.mode ?? d.state} />
    </div>
  );
}

const Index = () => {
  const { data, isLoading, error } = useApi<DevicesResponse>("/devices", {
    refetchInterval: 4000,
  });

  const adb = data?.adb ?? [];
  const fastboot = data?.fastboot ?? [];
  const usb = data?.usb ?? [];
  const ios = data?.ios ?? [];
  const allDevices = [...adb, ...fastboot, ...usb, ...ios];
  const primary = allDevices[0];
  const connected = allDevices.length > 0;

  return (
    <AppShell title="Dashboard">
      <div className="grid grid-cols-12 gap-5">
        {/* Device Panel */}
        <div className="col-span-12 lg:col-span-8">
          <GlassCard className="p-6 relative overflow-hidden" hover={false}>
            <div className="absolute -right-10 -top-10 w-72 h-72 bg-primary/20 rounded-full blur-3xl" />
            <div className="flex items-start justify-between mb-6 relative">
              <div>
                <p className="text-xs text-muted-foreground uppercase tracking-wider">Live Device Panel</p>
                <h2 className="text-2xl font-semibold mt-1">
                  {primary
                    ? `${primary.manufacturer ?? "Device"} · ${primary.mode ?? primary.state ?? "?"}`
                    : "No device connected"}
                </h2>
                <p className="text-sm text-muted-foreground mt-1">
                  {primary
                    ? `${primary.serial ?? primary.vendor_id ?? "—"} · ${primary.product ?? "unknown"}`
                    : "Waiting for device detection…"}
                </p>
              </div>
              <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium border ${connected ? "bg-success/15 text-success border-success/20" : "bg-destructive/15 text-destructive border-destructive/20"}`}>
                <span className={`w-2 h-2 rounded-full ${connected ? "bg-success" : "bg-destructive"} animate-pulse-glow`} />
                {connected ? "Online" : "Offline"}
              </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 relative">
              {[
                { icon: Cpu,       label: "Mode",     value: primary?.mode ?? primary?.state ?? "None" },
                { icon: HardDrive, label: "USB",       value: `${usb.length} device${usb.length !== 1 ? "s" : ""}` },
                { icon: Battery,   label: "ADB",       value: `${adb.length} device${adb.length !== 1 ? "s" : ""}` },
                { icon: Wifi,      label: "Fastboot",  value: `${fastboot.length} device${fastboot.length !== 1 ? "s" : ""}` },
              ].map(({ icon: Icon, label, value }) => (
                <div key={label} className="glass rounded-2xl p-4">
                  <Icon className="w-4 h-4 text-primary mb-2" />
                  <p className="text-xs text-muted-foreground">{label}</p>
                  <p className="text-sm font-semibold mt-0.5 truncate">{value}</p>
                </div>
              ))}
            </div>

            <div className="mt-6 grid grid-cols-2 gap-3 relative">
              <button className="bg-gradient-primary text-primary-foreground rounded-2xl py-3.5 font-medium glow-primary hover:scale-[1.02] transition">
                Read Info
              </button>
              <button className="glass-strong rounded-2xl py-3.5 font-medium hover:bg-white/5 transition">
                Reboot
              </button>
              <button className="col-span-2 rounded-2xl py-3.5 font-medium border border-destructive/30 bg-destructive/10 text-destructive hover:bg-destructive/15 transition">
                Disconnect
              </button>
            </div>
          </GlassCard>
        </div>

        {/* Side stats */}
        <div className="col-span-12 lg:col-span-4 space-y-5">
          <GlassCard title="All Devices">
            {isLoading ? (
              <p className="text-sm text-muted-foreground">Scanning…</p>
            ) : error ? (
              <p className="text-sm text-destructive">Backend unreachable</p>
            ) : allDevices.length === 0 ? (
              <p className="text-sm text-muted-foreground">No devices detected</p>
            ) : (
              <div className="space-y-1.5">
                {adb.map((d, i) => <DeviceRow key={`adb-${i}`} d={d} platform="android" />)}
                {fastboot.map((d, i) => <DeviceRow key={`fb-${i}`} d={d} platform="android" />)}
                {usb.map((d, i) => <DeviceRow key={`usb-${i}`} d={d} platform="android" />)}
                {ios.map((d, i) => <DeviceRow key={`ios-${i}`} d={d} platform="ios" />)}
              </div>
            )}
          </GlassCard>

          <GlassCard title="System Status">
            <div className="space-y-3">
              {[
                { label: "ADB Server",       ok: adb.length > 0 || !error },
                { label: "Fastboot",         ok: fastboot.length > 0 },
                { label: "USB (EDL/MTK/DL)", ok: usb.length > 0 },
                { label: "iOS",              ok: ios.length > 0 },
              ].map((s) => (
                <div key={s.label} className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">{s.label}</span>
                  {s.ok
                    ? <CheckCircle2 className="w-4 h-4 text-success" />
                    : <XCircle className="w-4 h-4 text-muted-foreground/40" />}
                </div>
              ))}
            </div>
          </GlassCard>
        </div>

        {/* Quick tools */}
        <div className="col-span-12">
          <h3 className="text-sm font-semibold mb-3 px-1">Quick Tools</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-4 gap-4">
            {[
              { to: "/tools/edl-loader",        icon: HardDrive, title: "EDL Loader",        desc: "Qualcomm firehose loaders" },
              { to: "/tools/adb-enabler",        icon: Zap,       title: "ADB Enabler",       desc: "Unlock developer mode" },
              { to: "/tools/boot-download",      icon: Smartphone,title: "Boot → Download",   desc: "Force download mode" },
              { to: "/tools/frp-bypass",         icon: Shield,    title: "FRP Bypass",        desc: "Factory reset protection" },
              { to: "/tools/flash",              icon: Download,  title: "Flash Tool",        desc: "Flash firmware images" },
              { to: "/tools/unlock",             icon: KeyRound,  title: "Unlock",            desc: "Bootloader unlock" },
              { to: "/tools/activation-removal", icon: Activity,  title: "Activation Removal",desc: "iOS activation lock" },
              { to: "/tools/passcode-bypass",    icon: Terminal,  title: "Passcode Bypass",   desc: "Bypass passcode screen" },
            ].map(({ to, icon: Icon, title, desc }) => (
              <NavLink key={to} to={to}>
                <GlassCard className="h-full">
                  <div className="w-10 h-10 rounded-xl bg-gradient-primary/20 border border-primary/30 flex items-center justify-center mb-3">
                    <Icon className="w-5 h-5 text-primary" />
                  </div>
                  <p className="font-medium text-sm">{title}</p>
                  <p className="text-xs text-muted-foreground mt-1">{desc}</p>
                </GlassCard>
              </NavLink>
            ))}
          </div>
        </div>

        {/* Live counts */}
        <div className="col-span-12 lg:col-span-5">
          <GlassCard title="Live Device Counts">
            <div className="space-y-3 text-sm">
              {[
                { label: "ADB (all states)",    count: adb.length },
                { label: "Fastboot",            count: fastboot.length },
                { label: "USB (EDL/MTK/DL/MTP)",count: usb.length },
                { label: "iOS",                 count: ios.length },
              ].map(({ label, count }) => (
                <div key={label} className="flex items-center justify-between">
                  <span className="text-muted-foreground">{label}</span>
                  <span className={count > 0 ? "text-success font-semibold" : ""}>{count}</span>
                </div>
              ))}
              <div className="rounded-2xl p-3 bg-white/5 mt-2">
                <p className="text-xs text-muted-foreground">Last refresh</p>
                <p className="mt-1 text-sm">{new Date().toLocaleTimeString()}</p>
              </div>
            </div>
          </GlassCard>
        </div>
      </div>
    </AppShell>
  );
};

export default Index;
