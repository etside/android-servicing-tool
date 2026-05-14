import { ToolPageLayout } from "@/components/tools/ToolPageLayout";

export default function EdlLoader() {
  return (
    <ToolPageLayout
      title="EDL Loader Parse"
      subtitle="Firmware Tools"
      description="Parse Beagle/TXT/binary captures and reconstruct Qualcomm Firehose loader ELF files. Supports cmd 0x03 and 0x12 sequences."
      inputLabel="Capture File (.bin / .txt)"
      outputLabel="Extraction Log"
      runLabel="Extract Loader"
      onRun={(i) => `loader.elf written from ${i}`}
    />
  );
}
