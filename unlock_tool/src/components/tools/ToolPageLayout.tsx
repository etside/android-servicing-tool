import { ReactNode, useState } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { GlassCard } from "@/components/ui/glass-card";
import { Upload, Play, Terminal as TerminalIcon } from "lucide-react";
import { toast } from "sonner";

export const ToolPageLayout = ({
  title,
  subtitle,
  description,
  children,
  inputLabel = "Input File",
  outputLabel = "Output",
  runLabel = "Run Tool",
  onRun,
}: {
  title: string,
  subtitle: string,
  description: string,
  children?: ReactNode,
  inputLabel?: string,
  outputLabel?: string,
  runLabel?: string,
  onRun?: (input: string) => string | Promise<string>,
}) => {
  const [input, setInput] = useState("");
  const [logs, setLogs] = useState<string[]>([
    "[ready] tool initialized",
    "[ready] waiting for input…",
  ]);
  const [running, setRunning] = useState(false);

  const handleRun = async () => {
    if (!input) {
      toast.error("Provide an input first");
      return;
    }
    setRunning(true);
    setLogs((l) => [...l, `[run] ${title} started`, `[info] processing ${input}`]);

    try {
      const result = onRun ? await onRun(input) : `Processed ${input}`;
      setLogs((l) => [...l, `[ok] ${result}`, "[done] completed in 412ms"]);
      toast.success(`${title} completed`);
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unexpected error";
      setLogs((l) => [...l, `[error] ${message}`]);
      toast.error(message);
    } finally {
      setRunning(false);
    }
  };

  return (
    <AppShell title={subtitle}>
      <div className="mb-6">
        <h2 className="text-2xl font-semibold">{title}</h2>
        <p className="text-sm text-muted-foreground mt-1 max-w-2xl">{description}</p>
      </div>

      <div className="grid grid-cols-12 gap-5">
        <div className="col-span-12 lg:col-span-7 space-y-5">
          <GlassCard title={inputLabel} hover={false}>
            <div className="space-y-3">
              <div className="flex gap-2">
                <input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="path/to/file or device identifier"
                  className="flex-1 bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm outline-none focus:border-primary/50 transition"
                />
                <button className="glass-strong rounded-xl px-4 hover:bg-white/10 transition flex items-center gap-2 text-sm">
                  <Upload className="w-4 h-4" /> Browse
                </button>
              </div>
              {children}
              <button
                onClick={handleRun}
                disabled={running}
                className="w-full bg-gradient-primary text-primary-foreground rounded-xl py-3.5 font-medium glow-primary hover:scale-[1.01] transition flex items-center justify-center gap-2 disabled:opacity-60"
              >
                <Play className="w-4 h-4" />
                {running ? "Running…" : runLabel}
              </button>
            </div>
          </GlassCard>

          <GlassCard title="Options">
            <div className="grid grid-cols-2 gap-3 text-sm">
              {["Verbose logging", "Auto-detect device", "Save report", "Notify on done"].map((o) => (
                <label key={o} className="flex items-center gap-3 p-3 rounded-xl bg-white/[0.03] cursor-pointer hover:bg-white/[0.06] transition">
                  <input type="checkbox" defaultChecked className="accent-primary w-4 h-4" />
                  <span>{o}</span>
                </label>
              ))}
            </div>
          </GlassCard>
        </div>

        <div className="col-span-12 lg:col-span-5">
          <GlassCard title={outputLabel} hover={false} className="h-full">
            <div className="bg-black/40 border border-white/5 rounded-xl p-4 font-mono text-xs h-[420px] overflow-auto scrollbar-hide">
              <div className="flex items-center gap-2 mb-3 text-muted-foreground">
                <TerminalIcon className="w-3 h-3" />
                <span>console</span>
              </div>
              {logs.map((l, i) => (
                <div key={i} className="text-foreground/80 leading-relaxed">
                  <span className="text-primary">›</span> {l}
                </div>
              ))}
            </div>
          </GlassCard>
        </div>
      </div>
    </AppShell>
  );
};
