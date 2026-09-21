import { useEffect, useMemo, useState } from "react";
import {
  ArrowDown,
  ArrowRight,
  Check,
  ChevronRight,
  ExternalLink,
  FileText,
  HelpCircle,
  Info,
  LockKeyhole,
  Quote,
  Scale,
} from "lucide-react";
import { Link, useRoute } from "wouter";

import { getBusinessProfile } from "../api/businessProfiles";
import { getPolicyChangeDetail } from "../api/policyChanges";
import { DEMO_CONFIG } from "../config/demo";
import StatusPill, { ChangeKindPill } from "../components/StatusPill";
import { TextButton } from "../components/PageHeader";
import type {
  BusinessProfile,
  ClaimDetail,
  PolicyChangeDetail,
} from "../types";

function formatDate(value: string | null | undefined) {
  if (!value) return "Not provided";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function getTrustState(
  change: PolicyChangeDetail,
): "CONFIRMED" | "REQUIRES_REVIEW" | "UNKNOWN" {
  const correspondenceStatus =
    change.correspondence?.status?.toUpperCase();

  if (
    correspondenceStatus === "PENDING" ||
    correspondenceStatus === "REQUIRES_REVIEW" ||
    correspondenceStatus === "UNCERTAIN"
  ) {
    return "REQUIRES_REVIEW";
  }

  if (
    change.old_claim?.status?.toUpperCase() === "ACTIVE" &&
    change.new_claim?.status?.toUpperCase() === "ACTIVE"
  ) {
    return "CONFIRMED";
  }

  return "UNKNOWN";
}

function ClaimEvidence({
  claim,
  label,
}: {
  claim: ClaimDetail;
  label: string;
}) {
  const evidence = claim.evidence[0];
  const document = claim.section.document;
  const source = document.source;

  return (
    <div className="rounded-2xl border border-[#dce6e8] bg-white p-6 md:p-7">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <div className="label-caps">{label}</div>

          <h2 className="mt-2 font-display text-[21px] font-semibold tracking-[-0.03em] text-[#254b5c]">
            Source evidence
          </h2>
        </div>

        <span className="inline-flex items-center gap-1.5 rounded-full border border-[#dbe7e6] bg-[#f5faf8] px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.1em] text-[#4d7d76]">
          <FileText size={13} />
          Evidence-backed
        </span>
      </div>

      <div className="mt-6 grid gap-4 border-y border-[#e9eff0] py-5 sm:grid-cols-2">
        <div>
          <div className="label-caps">Source</div>

          <div className="mt-2 flex items-center gap-2 text-[12px] font-semibold text-[#426373]">
            <FileText size={15} className="text-[#6c9599]" />
            {source.name}
          </div>
        </div>

        <div>
          <div className="label-caps">Location</div>

          <div className="mt-2 text-[12px] font-semibold text-[#426373]">
            {claim.section.section_number
              ? `Article ${claim.section.section_number}`
              : "Section not specified"}
            {evidence?.page != null
              ? ` · Page ${evidence.page}`
              : ""}
          </div>
        </div>
      </div>

      {evidence ? (
        <div className="relative mt-5 rounded-2xl border border-[#d9e7e6] bg-[#f6faf9] p-5 md:p-6">
          <Quote
            size={22}
            className="absolute right-5 top-5 text-[#a2c2bd]"
          />

          <div className="mb-3 text-[10px] font-bold uppercase tracking-[0.18em] text-[#6d9992]">
            Original source text
          </div>

          <blockquote className="max-w-3xl pr-8 font-serif text-[17px] leading-8 text-[#365b61]">
            “{evidence.quote}”
          </blockquote>

          <div className="mt-5 flex flex-wrap items-center justify-between gap-3 border-t border-[#dbe9e7] pt-4">
            <div className="text-[10px] text-[#819a9b]">
              {evidence.page != null
                ? `Preserved from page ${evidence.page} of the official document.`
                : "Evidence page not provided by the backend."}
            </div>

            {document.url ? (
              <a
                href={document.url}
                target="_blank"
                rel="noreferrer"
                className="inline-flex shrink-0 items-center gap-1.5 rounded-lg bg-[#245f68] px-3 py-2 text-[10px] font-bold text-white transition hover:bg-[#1e5159]"
              >
                <span>View official source</span>
                <ExternalLink size={12} />
              </a>
            ) : (
              <span className="rounded-lg border border-[#dce6e8] bg-white px-3 py-2 text-[10px] font-semibold text-[#8a9ca2]">
                Official source URL unavailable
              </span>
            )}
          </div>
        </div>
      ) : (
        <div className="mt-5 rounded-xl border border-dashed border-[#d6e2e4] bg-[#f8fbfb] p-5 text-[12px] text-[#819399]">
          No evidence item was returned for this claim.
        </div>
      )}
    </div>
  );
}

export default function RegulatoryChangeDetail() {
  const [, params] = useRoute("/changes/:id");

  const policyChangeId = params?.id ?? DEMO_CONFIG.policyChangeId;

  const [change, setChange] = useState<PolicyChangeDetail | null>(null);
  const [business, setBusiness] = useState<BusinessProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeStep, setActiveStep] = useState(0);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);

      try {
        const [changeResult, businessResult] = await Promise.all([
          getPolicyChangeDetail(policyChangeId),
          getBusinessProfile(DEMO_CONFIG.businessProfileId),
        ]);

        if (!cancelled) {
          setChange(changeResult);
          setBusiness(businessResult);
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error
              ? err.message
              : "Unable to load the regulatory change.",
          );
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    load();

    return () => {
      cancelled = true;
    };
  }, [policyChangeId]);

  const oldClaim = change?.old_claim ?? null;
  const newClaim = change?.new_claim ?? null;

  const trustState = useMemo(
    () => (change ? getTrustState(change) : "UNKNOWN"),
    [change],
  );

  const businessFacts = useMemo(() => {
    if (!business) return [];

    return business.entities.map((entity) => ({
      label: entity.entity_type.replaceAll("_", " "),
      value: entity.name,
    }));
  }, [business]);

  const provenance = useMemo(() => {
    if (!change) return [];

    return [
      {
        label: "Document",
        detail:
          newClaim?.section.document.title ??
          oldClaim?.section.document.title ??
          "Official document",
        status: "source",
      },
      {
        label: "Evidence",
        detail:
          newClaim?.evidence.length || oldClaim?.evidence.length
            ? "Claim is linked to source evidence returned by the backend."
            : "No evidence was returned for the selected claim.",
        status: "evidence",
      },
      {
        label: "Compared",
        detail:
          "The backend compared the previous and current claims and identified a modification to the requirement.",
        status: "derived",
      },
      {
        label: "Business context",
        detail: business
          ? "Business facts are loaded from the business-profile API. Applicability is not independently inferred by the frontend."
          : "Business profile unavailable.",
        status: "context",
      },
    ];
  }, [change, newClaim, oldClaim, business]);

  const selectedStep = provenance[activeStep] ?? provenance[0];

  if (loading) {
    return (
      <div className="page-enter mx-auto max-w-[1440px] px-5 py-10 md:px-8 lg:px-10">
        <div className="rounded-2xl border border-[#dce6e8] bg-white p-8 text-center text-[13px] text-[#7c9097]">
          Loading regulatory change...
        </div>
      </div>
    );
  }

  if (error || !change) {
    return (
      <div className="page-enter mx-auto max-w-[1100px] px-5 py-10 md:px-8 lg:px-10">
        <div className="rounded-2xl border border-[#ead6d3] bg-[#fdf8f7] p-8">
          <div className="flex items-center gap-2 text-[14px] font-semibold text-[#8e5e59]">
            <HelpCircle size={18} />
            Unable to load regulatory change
          </div>

          <p className="mt-2 text-[12px] leading-6 text-[#8b7774]">
            {error ?? "Regulatory change not found."}
          </p>

          <Link
            href="/changes"
            className="mt-5 inline-flex rounded-lg border border-[#d9e2e4] bg-white px-3 py-2 text-[11px] font-semibold text-[#54717b]"
          >
            Back to changes
          </Link>
        </div>
      </div>
    );
  }

  const primaryClaim = newClaim ?? oldClaim;
  const document = primaryClaim?.section.document;
  const section = primaryClaim?.section;

  return (
    <div className="page-enter mx-auto max-w-[1440px] px-5 py-7 md:px-8 md:py-10 lg:px-10">
      <header className="mb-9 border-b border-[#d7e2e4] pb-8">
        <div className="flex items-center justify-between gap-4">
          <Link
            href="/changes"
            className="inline-flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-[0.16em] text-[#78909a] transition hover:text-[#2b6871]"
          >
            <ArrowDown className="rotate-90" size={13} />
            All changes
          </Link>

          <StatusPill state={trustState} />
        </div>

        <div className="mt-7 max-w-5xl">
          <div className="text-[10px] font-bold uppercase tracking-[0.24em] text-[#7c9a9e]">
            Regulatory change
          </div>

          <h1 className="mt-3 font-display text-[30px] font-semibold leading-tight tracking-[-0.035em] text-[#173a50] md:text-[40px]">
            {document?.title ?? "Regulatory change"}
          </h1>

          <div className="mt-4 flex flex-wrap items-center gap-x-3 gap-y-2 text-[11px] text-[#71858d]">
            <span className="font-semibold text-[#496a75]">
              {section?.section_number
                ? `Article ${section.section_number}`
                : "Section not specified"}
            </span>

            <span className="text-[#b0bec1]">·</span>

            <span>
              Effective {formatDate(change.effective_date)}
            </span>

            <span className="text-[#b0bec1]">·</span>

            <span>
              Detected {formatDate(change.detected_at)}
            </span>
          </div>

          <p className="mt-6 max-w-3xl text-[13px] leading-7 text-[#657d86]">
            An existing regulatory requirement was modified. Review the previous
            and current claims below to see exactly what changed.
          </p>
        </div>
      </header>

      <section className="grid gap-5 xl:grid-cols-[minmax(0,1.35fr)_minmax(330px,0.65fr)]">
        <div className="border border-[#cfdfe2] bg-white">
          <div className="flex items-center justify-between border-b border-[#e1eaeb] px-6 py-4 md:px-8">
            <div className="flex items-center gap-3">
              <span className="h-1.5 w-1.5 rounded-full bg-[#5d938c]" />
              <span className="text-[10px] font-bold uppercase tracking-[0.2em] text-[#607c84]">
                Change detected
              </span>
            </div>

            <ChangeKindPill
              kind={
                change.change_type === "MODIFIED" ||
                change.change_type === "ADDED" ||
                change.change_type === "REMOVED"
                  ? change.change_type
                  : "REQUIRES_REVIEW"
              }
            />
          </div>

          <div className="grid md:grid-cols-[1fr_72px_1fr]">
            <div className="px-6 py-7 md:px-8 md:py-9">
              <div className="flex items-center justify-between gap-4">
                <div className="label-caps">
                  Previous requirement
                </div>

                <span className="text-[10px] font-medium uppercase tracking-[0.12em] text-[#9aa9ad]">
                  {oldClaim?.section.document.version_label ?? "Previous version"}
                </span>
              </div>

              <p className="mt-6 max-w-xl font-display text-[20px] font-semibold leading-8 tracking-[-0.025em] text-[#5d747c]">
                {oldClaim?.text ?? "No previous claim returned"}
              </p>

              {oldClaim && (
                <div className="mt-6 flex flex-wrap items-center gap-x-3 gap-y-1 border-t border-[#edf2f2] pt-4 text-[10px] uppercase tracking-[0.12em] text-[#94a3a8]">
                  {oldClaim.section.section_number && (
                    <span>
                      Article {oldClaim.section.section_number}
                    </span>
                  )}

                  {oldClaim.section.title && (
                    <>
                      <span className="text-[#c5d0d2]">·</span>
                      <span>{oldClaim.section.title}</span>
                    </>
                  )}
                </div>
              )}
            </div>

            <div className="flex items-center justify-center border-y border-[#e5eded] bg-[#fafcfc] px-4 py-4 md:border-y-0 md:border-x md:px-3">
              <div className="flex flex-col items-center gap-2">
                <ArrowRight
                  size={22}
                  strokeWidth={1.6}
                  className="text-[#6b9291]"
                />

                <span className="text-[8px] font-bold uppercase tracking-[0.18em] text-[#9aabad]">
                  Change
                </span>
              </div>
            </div>

            <div className="bg-[#f5faf8] px-6 py-7 md:px-8 md:py-9">
              <div className="flex items-center justify-between gap-4">
                <div className="label-caps text-[#4f8880]">
                  Current requirement
                </div>

                <span className="text-[10px] font-medium uppercase tracking-[0.12em] text-[#6f9995]">
                  {newClaim?.section.document.version_label ?? "Current version"}
                </span>
              </div>

              <p className="mt-6 max-w-xl font-display text-[20px] font-semibold leading-8 tracking-[-0.025em] text-[#1f6f72]">
                {newClaim?.text ?? "No current claim returned"}
              </p>

              {newClaim && (
                <div className="mt-6 flex flex-wrap items-center gap-x-3 gap-y-1 border-t border-[#dcebe7] pt-4 text-[10px] uppercase tracking-[0.12em] text-[#6e9794]">
                  {newClaim.section.section_number && (
                    <span>
                      Article {newClaim.section.section_number}
                    </span>
                  )}

                  {newClaim.section.title && (
                    <>
                      <span className="text-[#a9c1bf]">·</span>
                      <span>{newClaim.section.title}</span>
                    </>
                  )}
                </div>
              )}
            </div>
          </div>

          <div className="flex items-start gap-3 border-t border-[#e1eaeb] px-6 py-4 md:px-8">
            <Scale size={14} className="mt-0.5 shrink-0 text-[#6e9293]" />

            <p className="text-[11px] leading-5 text-[#74888e]">
              This comparison is the persisted result of the backend
              regulatory-change analysis. The frontend presents the
              determination; it does not infer the change.
            </p>
          </div>
        </div>
        <div className="rounded-2xl border border-[#dce6e8] bg-white p-6 md:p-7">
          <div className="flex items-start justify-between gap-4">
            <div>
              <div className="label-caps">Business context</div>

              <h2 className="mt-3 font-display text-[25px] font-semibold tracking-[-0.035em] text-[#235c5c]">
                {business?.name ?? "Business profile"}
              </h2>
            </div>

            <div className="grid h-9 w-9 shrink-0 place-items-center border border-[#dce6e8] bg-[#f8fbfb] text-[#71878d]">
              <HelpCircle size={17} />
            </div>
          </div>

          {businessFacts.length > 0 ? (
            <div className="mt-7 border-y border-[#e5eded]">
              {businessFacts.map((fact) => (
                <div
                  key={`${fact.label}-${fact.value}`}
                  className="flex items-center justify-between gap-5 border-b border-[#edf2f2] py-3.5 last:border-b-0"
                >
                  <span className="text-[10px] font-semibold uppercase tracking-[0.14em] text-[#8a9da1]">
                    {fact.label}
                  </span>

                  <span className="text-right text-[12px] font-semibold text-[#356b6b]">
                    {fact.value}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <div className="mt-7 border-y border-dashed border-[#dce6e8] py-5 text-[12px] text-[#819399]">
              No business facts were returned by the business-profile API.
            </div>
          )}

          <div className="mt-7">
            <div className="label-caps">Applicability</div>

            <div className="mt-3 border-l-2 border-[#b8c9cc] bg-[#f7fafa] px-4 py-3.5">
              <div className="text-[11px] font-semibold uppercase tracking-[0.12em] text-[#667f87]">
                Determination unavailable
              </div>

              <p className="mt-2 text-[11px] leading-5 text-[#74888e]">
                The current policy-change detail API does not expose a
                persisted applicability result for this regulatory change.
              </p>
            </div>
          </div>

          <div className="mt-5 flex items-start gap-2 text-[10px] leading-5 text-[#91a1a6]">
            <Info size={13} className="mt-0.5 shrink-0 text-[#78979a]" />

            <span>
              Business facts are shown as context. They are not treated as a
              legal applicability determination unless the backend provides
              that determination.
            </span>
          </div>
        </div>
      </section>

      <section className="mt-6 grid gap-5 xl:grid-cols-[minmax(0,1fr)_minmax(340px,0.7fr)]">
        <div className="space-y-5">
          {newClaim && (
            <ClaimEvidence claim={newClaim} label="Current claim" />
          )}

          {oldClaim && (
            <ClaimEvidence claim={oldClaim} label="Previous claim" />
          )}
        </div>

        <div className="rounded-2xl border border-[#dce6e8] bg-white p-6 md:p-7">
          <div className="flex items-start justify-between">
            <div>
              <div className="label-caps">Change metadata</div>

              <h2 className="mt-2 font-display text-[23px] font-semibold tracking-[-0.03em] text-[#254b5c]">
                Regulatory record
              </h2>
            </div>

            <LockKeyhole size={18} className="text-[#88a0a7]" />
          </div>

          <div className="mt-6 space-y-4">
            <div>
              <div className="label-caps">Change type</div>

              <div className="mt-1.5 text-[12px] font-semibold text-[#426373]">
                {change.change_type}
              </div>
            </div>

            <div>
              <div className="label-caps">Section</div>

              <div className="mt-1.5 text-[12px] font-semibold text-[#426373]">
                {section?.section_number
                  ? `Article ${section.section_number}`
                  : "Not provided"}
                {section?.title ? ` · ${section.title}` : ""}
              </div>
            </div>

            <div>
              <div className="label-caps">Document</div>

              <div className="mt-1.5 text-[12px] font-semibold leading-5 text-[#426373]">
                {document?.title ?? "Not provided"}
              </div>
            </div>

            <div>
              <div className="label-caps">Version</div>

              <div className="mt-1.5 text-[12px] font-semibold text-[#426373]">
                {document?.version_label ?? "Not provided"}
              </div>
            </div>

            <div>
              <div className="label-caps">Publication date</div>

              <div className="mt-1.5 text-[12px] font-semibold text-[#426373]">
                {formatDate(document?.publication_date)}
              </div>
            </div>

            <div>
              <div className="label-caps">Effective date</div>

              <div className="mt-1.5 text-[12px] font-semibold text-[#426373]">
                {formatDate(document?.effective_date)}
              </div>
            </div>

            <div>
              <div className="label-caps">Correspondence</div>

              <div className="mt-1.5 text-[12px] font-semibold text-[#426373]">
                {change.correspondence?.status ?? "Not provided"}
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="mt-6 rounded-2xl border border-[#dce6e8] bg-white p-6 md:p-7">
        <div className="flex flex-col gap-4 border-b border-[#e7edef] pb-5 md:flex-row md:items-end md:justify-between">
          <div>
            <div className="label-caps">Provenance chain</div>

            <h2 className="mt-2 font-display text-[23px] font-semibold tracking-[-0.03em] text-[#254b5c]">
              Where did this result come from?
            </h2>

            <p className="mt-2 text-[12px] text-[#819198]">
              Inspect the path from the official document to the persisted
              policy-change result.
            </p>
          </div>

          <div className="flex items-center gap-2 text-[10px] text-[#94a5aa]">
            <span className="h-1.5 w-1.5 rounded-full bg-[#d0a46b]" />
            Backend-derived record
          </div>
        </div>

        {provenance.length > 0 && (
          <>
            <div className="mt-6 grid gap-5 lg:grid-cols-[1.5fr_1fr]">
              <div className="flex flex-wrap items-center gap-x-1 gap-y-3 lg:flex-nowrap">
                {provenance.map((item, index) => (
                  <div key={item.label} className="flex items-center">
                    <button
                      onClick={() => setActiveStep(index)}
                      className={`group flex min-w-[90px] flex-col items-center gap-2 rounded-xl px-2 py-2 text-center transition ${
                        activeStep === index
                          ? "bg-[#edf5f4]"
                          : "hover:bg-[#f6f9f9]"
                      }`}
                    >
                      <span
                        className={`grid h-9 w-9 place-items-center rounded-full border text-[11px] font-bold ${
                          activeStep === index
                            ? "border-[#8dc0b7] bg-[#dff0eb] text-[#31756e]"
                            : "border-[#d6e3e5] bg-white text-[#77909a]"
                        }`}
                      >
                        {index + 1}
                      </span>

                      <span
                        className={`text-[9px] font-bold uppercase tracking-[0.1em] ${
                          activeStep === index
                            ? "text-[#31756e]"
                            : "text-[#91a1a6]"
                        }`}
                      >
                        {item.label}
                      </span>
                    </button>

                    {index < provenance.length - 1 && (
                      <ChevronRight
                        size={14}
                        className="mx-0.5 hidden text-[#b1c2c5] sm:block"
                      />
                    )}
                  </div>
                ))}
              </div>

              {selectedStep && (
                <div className="rounded-xl border border-[#e1ebec] bg-[#f8fbfb] p-5">
                  <div className="label-caps">Selected step</div>

                  <div className="mt-2 flex items-center gap-2 text-[14px] font-semibold text-[#31596a]">
                    <span className="grid h-6 w-6 place-items-center rounded-md bg-[#dfefec] text-[11px] text-[#3e8179]">
                      {activeStep + 1}
                    </span>

                    {selectedStep.label}
                  </div>

                  <p className="mt-2 text-[12px] leading-6 text-[#789097]">
                    {selectedStep.detail}
                  </p>

                  <div className="mt-4 flex items-center gap-1.5 text-[10px] font-semibold text-[#56867f]">
                    <Check size={13} />

                    {selectedStep.status === "source"
                      ? "Source metadata"
                      : selectedStep.status === "evidence"
                        ? "Evidence linkage"
                        : selectedStep.status === "derived"
                          ? "Backend comparison"
                          : "Business context"}
                  </div>
                </div>
              )}
            </div>

            <div className="mt-7 flex items-center gap-2 border-t border-[#edf1f2] pt-4 text-[11px] text-[#91a1a6]">
              <ArrowDown size={14} className="text-[#86aaa8]" />

              The backend remains the source of truth for regulatory
              comparison and any future applicability determination.
            </div>
          </>
        )}
      </section>

      <div className="mt-5 flex items-center justify-between text-[11px] text-[#96a6aa]">
        <div className="flex items-center gap-2">
          <span className="h-1.5 w-1.5 rounded-full bg-[#d0a46b]" />
          Evidence-centered regulatory record
        </div>

        <TextButton onClick={() => window.print()}>
          Print evidence view
        </TextButton>
      </div>
    </div>
  );
}
