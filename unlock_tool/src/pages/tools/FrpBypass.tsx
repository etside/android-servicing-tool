import { ToolPageLayout } from "@/components/tools/ToolPageLayout";

export default function FrpBypass() {
  return (
    <ToolPageLayout
      title="FRP Bypass"
      subtitle="Android Security Tools"
      description="Attempt a factory reset protection bypass flow for supported Qualcomm devices. Use this only on authorized devices."
      inputLabel="Device serial or identifier"
      outputLabel="Bypass Log"
      runLabel="Start FRP Bypass"
      onRun={async (input) => {
        const response = await fetch("/api/tool/frp-bypass", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ input }),
        });
        if (!response.ok) {
          throw new Error("Failed to start FRP bypass");
        }
        const data = await response.json();
        return data.message || "FRP bypass queued";
      }}
    />
  );
}
