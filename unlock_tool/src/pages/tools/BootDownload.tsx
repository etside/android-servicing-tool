import { ToolPageLayout } from "@/components/tools/ToolPageLayout";

export default function BootDownload() {
  return (
    <ToolPageLayout
      title="Boot → Download"
      subtitle="Mode Switch"
      description="Send the boot-to-download sequence and place a connected modem into Qualcomm 9008 EDL/Sahara mode automatically."
      inputLabel="Device Port"
      outputLabel="USB Trace"
      runLabel="Trigger Download Mode"
      onRun={(i) => `device on ${i} switched to 9008`}
    />
  );
}
