import { ToolPageLayout } from "@/components/tools/ToolPageLayout";

export default function ActivationRemoval() {
  return (
    <ToolPageLayout
      title="iOS Activation Removal"
      subtitle="iOS Device Recovery"
      description="Attempt an activation lock cleanup for supported iOS devices. This tool is intended for recovery workflows only."
      inputLabel="Device UDID or serial"
      outputLabel="Activation Removal Log"
      runLabel="Start Activation Removal"
      onRun={async (input) => {
        const response = await fetch("/api/tool/activation-removal", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ input }),
        });
        if (!response.ok) {
          throw new Error("Failed to start activation removal");
        }
        const data = await response.json();
        return data.message || "Activation removal queued";
      }}
    />
  );
}
