import { AlertCircle, Check, HelpCircle, ShieldCheck } from "lucide-react";
import type { TrustState } from "../types";

const labels: Record<TrustState, string> = {
  CONFIRMED: "Confirmed",
  REQUIRES_REVIEW: "Requires review",
  SUPPORTED: "Supported",
  UNSUPPORTED: "Unsupported",
  UNKNOWN: "Unknown",
  APPLIES: "Applies to business",
  DOES_NOT_APPLY: "Does not apply",
};

const styles: Record<TrustState, string> = {
  CONFIRMED: "bg-[#e7f4ef] text-[#247061] border-[#c5e4d9]",
  SUPPORTED: "bg-[#edf5f4] text-[#2d6b70] border-[#cfe3e3]",
  APPLIES: "bg-[#e7f4ef] text-[#247061] border-[#c5e4d9]",
  REQUIRES_REVIEW: "bg-[#f6f1e8] text-[#8a6841] border-[#eadcc6]",
  UNKNOWN: "bg-[#f2f4f5] text-[#687b83] border-[#dde4e6]",
  UNSUPPORTED: "bg-[#f5ecea] text-[#925f59] border-[#ebd6d2]",
  DOES_NOT_APPLY: "bg-[#f2f4f5] text-[#687b83] border-[#dde4e6]",
};

function StateIcon({ state }: { state: TrustState }) {
  if (state === "CONFIRMED" || state === "APPLIES") return <Check size={12} strokeWidth={2.8} />;
  if (state === "REQUIRES_REVIEW") return <AlertCircle size={12} />;
  if (state === "UNKNOWN") return <HelpCircle size={12} />;
  return <ShieldCheck size={12} />;
}

export default function StatusPill({ state, compact = false }: { state: TrustState; compact?: boolean }) {
  return <span className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.12em] ${styles[state]} ${compact ? "px-2 py-0.5 text-[9px]" : ""}`}><StateIcon state={state} />{labels[state]}</span>;
}

export function ChangeKindPill({ kind }: { kind: "MODIFIED" | "ADDED" | "REMOVED" | "REQUIRES_REVIEW" }) {
  const palette = {
    MODIFIED: "bg-[#e8f0f5] text-[#3c687b] border-[#cfdee6]",
    ADDED: "bg-[#edf5ed] text-[#477052] border-[#d6e7d5]",
    REMOVED: "bg-[#f4eceb] text-[#925f59] border-[#e8d4d1]",
    REQUIRES_REVIEW: "bg-[#f6f1e8] text-[#8a6841] border-[#eadcc6]",
  }[kind];
  return <span className={`inline-flex rounded-full border px-2.5 py-1 text-[10px] font-bold tracking-[0.15em] ${palette}`}>{kind.replace("_", " ")}</span>;
}
