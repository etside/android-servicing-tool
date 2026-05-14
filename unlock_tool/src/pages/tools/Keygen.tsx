import { ToolPageLayout } from "@/components/tools/ToolPageLayout";

export default function Keygen() {
  return (
    <ToolPageLayout
      title="Sierra Keygen"
      subtitle="OEM Unlock"
      description="Generate AT!OPENLOCK / AT!OPENCND response keys for Sierra Wireless modems from a 16-char challenge string."
      inputLabel="Challenge String"
      outputLabel="Key Response"
      runLabel="Generate Key"
      onRun={(i) => `key for "${i}": A1B2C3D4E5F60718`}
    />
  );
}
