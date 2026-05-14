import { ToolPageLayout } from "@/components/tools/ToolPageLayout";

export default function AdbEnabler() {
  return (
    <ToolPageLayout
      title="ADB Enabler"
      subtitle="Device Unlock"
      description="Enable ADB / developer mode on Sierra, Quectel, ZTE, Netgear and Telit modules through AT/Telnet command channels."
      inputLabel="Device Port (COMx / IP)"
      outputLabel="Session Log"
      runLabel="Enable ADB"
      onRun={(i) => `ADB enabled on ${i}`}
    />
  );
}
