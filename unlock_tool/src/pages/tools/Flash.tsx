import { ToolPageLayout } from "@/components/tools/ToolPageLayout";

export default function Flash() {
  return (
    <ToolPageLayout
      title="Flash Tool"
      subtitle="Android Firmware Operations"
      description="Flash firmware images to connected devices in fastboot or download mode. Provide a target image path or device identifier."
      inputLabel="Image path or device serial"
      outputLabel="Flash Output"
      runLabel="Submit Flash"
      onRun={async (input) => {
        const response = await fetch("/api/tool/flash", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ input }),
        });
        if (!response.ok) {
          throw new Error("Failed to queue flash operation");
        }
        const data = await response.json();
        return data.message || "Flash operation queued";
      }}
    />
  );
}
