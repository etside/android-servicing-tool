import { ToolPageLayout } from "@/components/tools/ToolPageLayout";

export default function PasscodeBypass() {
  return (
    <ToolPageLayout
      title="Passcode Bypass"
      subtitle="iOS Security Tools"
      description="Attempt a safe passcode bypass routine for supported devices. Use this tool only after verifying user authorization."
      inputLabel="Device UDID or passcode hint"
      outputLabel="Bypass Trace"
      runLabel="Run Passcode Bypass"
      onRun={async (input) => {
        const response = await fetch("/api/tool/passcode-bypass", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ input }),
        });
        if (!response.ok) {
          throw new Error("Failed to start passcode bypass");
        }
        const data = await response.json();
        return data.message || "Passcode bypass queued";
      }}
    />
  );
}
