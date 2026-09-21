import {
  AlertCircle,
  ArrowRight,
  CheckCircle2,
  FileWarning,
  GitCompareArrows,
  ShieldQuestion,
} from "lucide-react";
import { useEffect, useState } from "react";

import { getPolicyChangeDetail } from "../api/policyChanges";
import { DEMO_CONFIG } from "../config/demo";
import { PageHeader } from "../components/PageHeader";
import StatusPill from "../components/StatusPill";
import type { PolicyChangeDetail } from "../types";

export default function Review() {
  const [change, setChange] = useState<PolicyChangeDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    getPolicyChangeDetail(DEMO_CONFIG.policyChangeId)
      .then((result) => {
        if (!cancelled) {
          setChange(result);
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setError(
            err instanceof Error
              ? err.message
              : "Unable to load review information.",
          );
        }
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, []);

  if (loading) {
    return (
      <div className="page-enter mx-auto max-w-[1040px] px-5 py-10 md:px-8 lg:px-10">
        <div className="rounded-2xl border border-[#dce6e8] bg-white p-8 text-center text-[13px] text-[#7c9097]">
          Loading review status...
        </div>
      </div>
    );
  }

  if (error || !change) {
    return (
      <div className="page-enter mx-auto max-w-[1040px] px-5 py-10 md:px-8 lg:px-10">
        <div className="rounded-2xl border border-[#ead6d3] bg-[#fdf8f7] p-8">
          <h2 className="text-[14px] font-semibold text-[#8e5e59]">
            Review information unavailable
          </h2>
          <p className="mt-2 text-[12px] leading-6 text-[#8b7774]">
            {error ?? "The policy-change review information could not be loaded."}
          </p>
        </div>
      </div>
    );
  }

  const correspondence = change.correspondence;
  const oldClaim = change.old_claim;
  const newClaim = change.new_claim;

  const reviewState =
    correspondence?.status === "PENDING"
      ? "REQUIRES_REVIEW"
      : correspondence?.status === "MATCHED"
        ? "CONFIRMED"
        : "UNKNOWN";

  return (
    <div className="page-enter mx-auto max-w-[1040px] px-5 py-7 md:px-8 md:py-10 lg:px-10">
      <PageHeader
        eyebrow="Human review"
        title="Review status"
        description="The interface preserves uncertainty from the regulatory intelligence pipeline instead of turning an unresolved state into a false confirmation."
        actions={
          <StatusPill
            state={reviewState}
            compact
          />
        }
      />

      <div className="space-y-5">
        <section className="rounded-2xl border border-[#e5dcca] bg-[#fdfaf5] p-6 md:p-7">
          <div className="flex items-start gap-3">
            <div className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-[#f4ead8] text-[#98754c]">
              {reviewState === "CONFIRMED" ? (
                <CheckCircle2 size={19} />
              ) : (
                <FileWarning size={19} />
              )}
            </div>

            <div>
              <h2 className="font-display text-[23px] font-semibold tracking-[-0.03em] text-[#664f36]">
                {correspondence?.status === "PENDING"
                  ? "Correspondence requires review"
                  : "Correspondence status"}
              </h2>

              <p className="mt-1 text-[12px] leading-6 text-[#8c785e]">
                {correspondence?.status === "PENDING"
                  ? "The backend has not recorded a human resolution for this correspondence."
                  : `Backend correspondence status: ${correspondence?.status ?? "UNKNOWN"}.`}
              </p>
            </div>
          </div>

          <div className="mt-6 grid gap-3 lg:grid-cols-[1fr_auto_1fr]">
            <div className="rounded-xl border border-[#eadfcf] bg-white/80 p-5">
              <div className="label-caps text-[#a38865]">Old claim</div>

              <p className="mt-3 text-[13px] leading-6 text-[#765e43]">
                {oldClaim?.text ?? "No previous claim available."}
              </p>

              {oldClaim && (
                <div className="mt-4 text-[10px] uppercase tracking-[0.12em] text-[#a38865]">
                  Section {oldClaim.section.section_number ?? "Unavailable"}
                </div>
              )}
            </div>

            <div className="flex items-center justify-center text-[#bf9a6b]">
              <GitCompareArrows size={20} />
            </div>

            <div className="rounded-xl border border-[#dce6e8] bg-white p-5">
              <div className="label-caps text-[#66858e]">New claim</div>

              <p className="mt-3 text-[13px] leading-6 text-[#58747d]">
                {newClaim?.text ?? "No current claim available."}
              </p>

              {newClaim && (
                <div className="mt-4 text-[10px] uppercase tracking-[0.12em] text-[#66858e]">
                  Section {newClaim.section.section_number ?? "Unavailable"}
                </div>
              )}
            </div>
          </div>
        </section>

        <section className="grid gap-5 lg:grid-cols-[1fr_320px]">
          <div className="rounded-2xl border border-[#dce6e8] bg-white p-6">
            <div className="label-caps">Review context</div>

            <div className="mt-5 space-y-5">
              <div>
                <div className="label-caps">Relationship</div>
                <p className="mt-2 text-[13px] font-semibold text-[#3e6271]">
                  {correspondence?.relationship_type ?? "Unavailable"}
                </p>
              </div>

              <div>
                <div className="label-caps">Method</div>
                <p className="mt-2 text-[13px] font-semibold text-[#3e6271]">
                  {correspondence?.method ?? "Unavailable"}
                </p>
              </div>

              <div>
                <div className="label-caps">Confidence</div>
                <p className="mt-2 text-[13px] font-semibold text-[#3e6271]">
                  {correspondence?.confidence !== null &&
                  correspondence?.confidence !== undefined
                    ? `${Math.round(correspondence.confidence * 100)}%`
                    : "Unavailable"}
                </p>
                <p className="mt-1 text-[11px] leading-5 text-[#83979d]">
                  Confidence is not the same as human verification. The
                  backend status remains authoritative.
                </p>
              </div>

              <div>
                <div className="label-caps">Policy change</div>
                <p className="mt-2 text-[12px] leading-6 text-[#6f858d]">
                  {change.summary}
                </p>
              </div>
            </div>
          </div>

          <aside className="h-fit rounded-2xl border border-[#dce6e8] bg-[#f8fbfb] p-6">
            <div className="flex items-center gap-2">
              <ShieldQuestion size={16} className="text-[#638b94]" />
              <div className="label-caps">Human decision</div>
            </div>

            <p className="mt-4 text-[12px] leading-6 text-[#809198]">
              This frontend does not expose a fake review action. The current
              backend API does not provide a claim-correspondence decision
              endpoint.
            </p>

            <div className="mt-5 rounded-xl border border-[#dce6e8] bg-white p-4">
              <div className="flex items-start gap-2">
                <AlertCircle
                  size={15}
                  className="mt-0.5 shrink-0 text-[#9b7b51]"
                />

                <p className="text-[11px] leading-5 text-[#788d94]">
                  The unresolved state is intentionally preserved. Adding a
                  human decision here would require a backend contract first.
                </p>
              </div>
            </div>

            <div className="mt-5 flex items-center gap-2 text-[10px] font-semibold uppercase tracking-[0.12em] text-[#91a1a6]">
              View change
              <ArrowRight size={12} />
            </div>
          </aside>
        </section>
      </div>
    </div>
  );
}
