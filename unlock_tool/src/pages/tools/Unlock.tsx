import { ToolPageLayout } from "@/components/tools/ToolPageLayout";

export default function Unlock() {
  return (
    <ToolPageLayout
      title="Bootloader Unlock"
      subtitle="Android Unlock Utilities"
      description="Trigger unlock workflows for Qualcomm devices, including OEM unlock, bootloader unlock and secure partition access."
      inputLabel="Device serial or unlock token"
      outputLabel="Unlock Log"
      runLabel="Run Unlock"
      onRun={async (input) => {
        const response = await fetch("/api/tool/unlock", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ input }),
        });
        if (!response.ok) {
          throw new Error("Failed to start unlock operation");
        }
        const data = await response.json();
        return data.message || "Unlock operation queued";
      }}
    />
  );
}
