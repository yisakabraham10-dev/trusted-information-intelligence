import {
  ArrowRight,
  ArrowUpRight,
  CheckCircle2,
  Clock3,
  FileCheck2,
  LibraryBig,
  ShieldCheck,
} from "lucide-react";
import { Link } from "wouter";
import { getBusinessProfile } from "../api/businessProfiles";
import { getPolicyChangeDetail } from "../api/policyChanges";
import { ChangeKindPill, default as StatusPill } from "../components/StatusPill";
import { PageHeader } from "../components/PageHeader";
import { DEMO_CONFIG } from "../config/demo";
import type { BusinessProfile, PolicyChangeDetail } from "../types";
import { useEffect, useState } from "react";

function formatDate(value: string | null | undefined) {
  if (!value) return "Not specified";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat("en", {
    day: "numeric",
    month: "short",
    year: "numeric",
  }).format(date);
}

function getEntityValue(
  business: BusinessProfile | null,
  entityType: string,
) {
  return (
    business?.entities.find(
      (entity) => entity.entity_type.toUpperCase() === entityType,
    )?.name ?? "Not specified"
  );
}

function LoadingState() {
  return (
    <div className="page-enter mx-auto max-w-[1440px] px-5 py-10 md:px-8 lg:px-10">
      <div className="rounded-2xl border border-[#dce6e8] bg-white p-10 text-center">
        <div className="mx-auto h-8 w-8 animate-spin rounded-full border-2 border-[#d5e4e6] border-t-[#3d7480]" />
        <p className="mt-4 text-sm font-medium text-[#526d78]">
          Loading regulatory intelligence...
        </p>
      </div>
    </div>
  );
}

function ErrorState({ message }: { message: string }) {
  return (
    <div className="page-enter mx-auto max-w-[1440px] px-5 py-10 md:px-8 lg:px-10">
      <div className="rounded-2xl border border-[#ead6d2] bg-white p-8">
        <div className="flex items-start gap-3">
          <div className="grid h-9 w-9 shrink-0 place-items-center rounded-xl bg-[#f5ecea] text-[#925f59]">
            <Clock3 size={17} />
          </div>

          <div>
            <h2 className="font-display text-lg font-semibold text-[#294e5f]">
              Unable to load regulatory intelligence
            </h2>

            <p className="mt-2 text-sm leading-6 text-[#71848c]">
              {message}
            </p>

            <p className="mt-3 text-[11px] text-[#9aaaaf]">
              Check that the FastAPI backend is running and that
              VITE_API_BASE_URL points to it.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function Dashboard() {
  const [business, setBusiness] = useState<BusinessProfile | null>(null);
  const [change, setChange] = useState<PolicyChangeDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function loadDashboard() {
      try {
        setLoading(true);
        setError(null);

        const [businessProfile, policyChange] = await Promise.all([
          getBusinessProfile(DEMO_CONFIG.businessProfileId),
          getPolicyChangeDetail(DEMO_CONFIG.policyChangeId),
        ]);

        if (cancelled) return;

        setBusiness(businessProfile);
        setChange(policyChange);
      } catch (err) {
        if (cancelled) return;

        setError(
          err instanceof Error
            ? err.message
            : "Unable to connect to the regulatory intelligence service.",
        );
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadDashboard();

    return () => {
      cancelled = true;
    };
  }, []);

  if (loading) {
    return <LoadingState />;
  }

  if (error || !business || !change) {
    return (
      <ErrorState
        message={
          error ??
          "The regulatory change or business profile could not be loaded."
        }
      />
    );
  }

  const currentClaim = change.new_claim ?? change.old_claim;
  const oldClaim = change.old_claim;
  const newClaim = change.new_claim;

  const document = currentClaim?.section.document;
  const evidenceCount =
    (oldClaim?.evidence.length ?? 0) + (newClaim?.evidence.length ?? 0);

  const sourceName = document?.source.name ?? "Source unavailable";

  const businessActivity = getEntityValue(business, "ACTIVITY");
  const transportMode = getEntityValue(business, "TRANSPORT_MODE");

  return (
    <div className="page-enter mx-auto max-w-[1440px] px-5 py-7 md:px-8 md:py-10 lg:px-10">
      <PageHeader
        eyebrow="Overview"
        title="Regulatory intelligence"
        description={`Monitor changes that affect ${business.name.toLowerCase()}, with every conclusion tied back to official evidence.`}
        actions={
          <div className="flex items-center gap-2 rounded-full border border-[#dbe6e7] bg-white px-3.5 py-2 text-[11px] font-medium text-[#66808a]">
            <span className="h-1.5 w-1.5 rounded-full bg-[#45a18e]" />
            System operational
          </div>
        }
      />

      {/* Real API-backed summary */}
      <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <div className="soft-card rounded-2xl border border-[#dce6e8] bg-white p-5">
          <div className="mb-5 grid h-9 w-9 place-items-center rounded-xl bg-[#f8f1e7] text-[#8b6a44]">
            <Clock3 size={17} />
          </div>

          <div className="font-display text-[27px] font-semibold tracking-[-0.05em] text-[#173b51]">
            {change.change_type}
          </div>

          <div className="mt-1 text-[12px] font-semibold text-[#526d78]">
            Current change
          </div>

          <div className="mt-2 text-[11px] text-[#9aaaaf]">
            Status: {change.status}
          </div>
        </div>

        <div className="soft-card rounded-2xl border border-[#dce6e8] bg-white p-5">
          <div className="mb-5 grid h-9 w-9 place-items-center rounded-xl bg-[#e8f4ef] text-[#36786d]">
            <CheckCircle2 size={17} />
          </div>

          <div className="font-display text-[27px] font-semibold tracking-[-0.05em] text-[#173b51]">
            {evidenceCount}
          </div>

          <div className="mt-1 text-[12px] font-semibold text-[#526d78]">
            Evidence items
          </div>

          <div className="mt-2 text-[11px] text-[#9aaaaf]">
            Linked to the compared claims
          </div>
        </div>

        <div className="soft-card rounded-2xl border border-[#dce6e8] bg-white p-5">
          <div className="mb-5 grid h-9 w-9 place-items-center rounded-xl bg-[#edf1f3] text-[#637780]">
            <ShieldCheck size={17} />
          </div>

          <div className="font-display text-[27px] font-semibold tracking-[-0.05em] text-[#173b51]">
            {change.correspondence?.status ?? "UNKNOWN"}
          </div>

          <div className="mt-1 text-[12px] font-semibold text-[#526d78]">
            Correspondence status
          </div>

          <div className="mt-2 text-[11px] text-[#9aaaaf]">
            Backend determination
          </div>
        </div>

        <div className="soft-card rounded-2xl border border-[#dce6e8] bg-white p-5">
          <div className="mb-5 grid h-9 w-9 place-items-center rounded-xl bg-[#e8f0f5] text-[#4d7185]">
            <LibraryBig size={17} />
          </div>

          <div className="font-display text-[27px] font-semibold tracking-[-0.05em] text-[#173b51]">
            {business.tracked_sources.length}
          </div>

          <div className="mt-1 text-[12px] font-semibold text-[#526d78]">
            Sources tracked
          </div>

          <div className="mt-2 text-[11px] text-[#9aaaaf]">
            Configured for this business
          </div>
        </div>
      </section>

      {/* Primary regulatory change */}
      <section className="mt-8 grid gap-5 xl:grid-cols-[minmax(0,1fr)_320px]">
        <div className="overflow-hidden rounded-2xl border border-[#dce6e8] bg-white">
          <div className="flex items-center justify-between border-b border-[#e6edef] px-5 py-4 md:px-6">
            <div>
              <h2 className="font-display text-[19px] font-semibold text-[#24495b]">
                Relevant regulatory change
              </h2>

              <p className="mt-1 text-[11px] text-[#8a9ba2]">
                Loaded directly from the policy-change API
              </p>
            </div>

            <ChangeKindPill
              kind={
                change.change_type === "ADDED" ||
                change.change_type === "REMOVED" ||
                change.change_type === "REQUIRES_REVIEW"
                  ? change.change_type
                  : "MODIFIED"
              }
            />
          </div>

          <div className="px-5 py-6 md:px-6">
            <div className="text-[11px] font-medium uppercase tracking-[0.14em] text-[#91a1a6]">
              {document?.title ?? "Document unavailable"}
            </div>

            <h3 className="mt-2 text-xl font-semibold text-[#294e5f]">
              {newClaim?.section.title ??
                oldClaim?.section.title ??
                "Regulatory claim change"}
            </h3>

            <div className="mt-2 flex flex-wrap items-center gap-2 text-[11px] text-[#84979e]">
              <span>
                Article {currentClaim?.section.section_number ?? "not specified"}
              </span>

              <span>·</span>

              <span>{sourceName}</span>

              <span>·</span>

              <span>
                Effective {formatDate(change.effective_date)}
              </span>
            </div>

            <div className="mt-6 grid gap-3 md:grid-cols-[1fr_auto_1fr] md:items-stretch">
              <div className="rounded-2xl border border-[#e0e8ea] bg-[#f8fafb] p-5">
                <div className="text-[10px] font-bold uppercase tracking-[0.14em] text-[#91a1a6]">
                  Previous requirement
                </div>

                <p className="mt-3 text-[13px] leading-6 text-[#496672]">
                  {oldClaim?.text ?? "No previous claim available."}
                </p>

                <div className="mt-4 text-[10px] text-[#91a1a6]">
                  {oldClaim?.section.document.version_label ??
                    "Previous version unavailable"}
                </div>
              </div>

              <div className="hidden items-center justify-center text-[#91a1a6] md:flex">
                <ArrowRight size={20} />
              </div>

              <div className="rounded-2xl border border-[#cfe3dc] bg-[#f0f8f5] p-5">
                <div className="text-[10px] font-bold uppercase tracking-[0.14em] text-[#568276]">
                  Current requirement
                </div>

                <p className="mt-3 text-[13px] leading-6 text-[#355f65]">
                  {newClaim?.text ?? "No current claim available."}
                </p>

                <div className="mt-4 text-[10px] text-[#6d8f8d]">
                  {newClaim?.section.document.version_label ??
                    "Current version unavailable"}
                </div>
              </div>
            </div>

            <div className="mt-5 flex flex-wrap gap-3">
              <div className="rounded-full border border-[#dbe6e8] bg-[#f8fafb] px-3 py-1.5 text-[10px] font-semibold uppercase tracking-[0.12em] text-[#687f87]">
                Status: {change.status}
              </div>

              <div className="rounded-full border border-[#dbe6e8] bg-[#f8fafb] px-3 py-1.5 text-[10px] font-semibold uppercase tracking-[0.12em] text-[#687f87]">
                Detected: {formatDate(change.detected_at)}
              </div>
            </div>

            <Link
              href={`/changes/${change.id}`}
              className="mt-6 inline-flex items-center gap-2 rounded-xl bg-[#1d4056] px-4 py-3 text-[11px] font-bold text-white transition hover:bg-[#244c65]"
            >
              Open regulatory change
              <ArrowUpRight size={15} />
            </Link>
          </div>
        </div>

        {/* Evidence-first panel */}
        <aside className="rounded-2xl border border-[#dce6e8] bg-[#1d4056] p-6 text-white shadow-[0_14px_34px_rgba(29,64,86,0.14)]">
          <div className="flex items-center justify-between">
            <div className="grid h-9 w-9 place-items-center rounded-xl bg-white/10">
              <FileCheck2 size={18} />
            </div>

            <span className="rounded-full border border-white/15 bg-white/10 px-2.5 py-1 text-[9px] font-bold uppercase tracking-[0.16em] text-[#b9d9d5]">
              Evidence-first
            </span>
          </div>

          <h2 className="mt-7 font-display text-2xl font-semibold tracking-[-0.03em]">
            See the reason behind the change.
          </h2>

          <p className="mt-3 text-[12px] leading-6 text-[#b3c9d0]">
            AI assists with extraction. Evidence supports the claim.
            Deterministic logic compares versions.
          </p>

          <div className="mt-7 border-t border-white/10 pt-5">
            <div className="text-[10px] uppercase tracking-[0.18em] text-[#87adb7]">
              Correspondence
            </div>

            <div className="mt-2 text-sm font-medium text-[#f4f8f8]">
              {change.correspondence?.relationship_type ?? "Not available"}
            </div>

            <div className="mt-1 text-[11px] text-[#a9c1c8]">
              Status: {change.correspondence?.status ?? "UNKNOWN"}
            </div>

            {change.correspondence?.confidence !== null &&
              change.correspondence?.confidence !== undefined && (
                <div className="mt-1 text-[11px] text-[#a9c1c8]">
                  Confidence:{" "}
                  {Math.round(change.correspondence.confidence * 100)}%
                </div>
              )}
          </div>

          <Link
            href={`/changes/${change.id}`}
            className="mt-7 inline-flex items-center gap-2 rounded-xl bg-[#d9eee9] px-4 py-3 text-[11px] font-bold text-[#245e60] transition hover:bg-white"
          >
            <span>Open primary change</span>
            <ArrowUpRight size={15} />
          </Link>
        </aside>
      </section>

      {/* Business context + source */}
      <section className="mt-8 grid gap-5 lg:grid-cols-2">
        <div className="rounded-2xl border border-[#dce6e8] bg-white p-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="font-display text-[19px] font-semibold text-[#24495b]">
                Business context
              </h2>

              <p className="mt-1 text-[11px] text-[#8a9ba2]">
                Facts supplied by the business-profile API
              </p>
            </div>

            <Link
              href="/business-profile"
              className="text-[#3d7480] hover:text-[#205a68]"
            >
              <ArrowUpRight size={16} />
            </Link>
          </div>

          <div className="mt-6 grid grid-cols-2 gap-5">
            <div>
              <div className="label-caps">Business</div>
              <div className="mt-2 text-[13px] font-semibold text-[#385b68]">
                {business.name}
              </div>
            </div>

            <div>
              <div className="label-caps">Activity</div>
              <div className="mt-2 text-[13px] font-semibold text-[#385b68]">
                {businessActivity}
              </div>
            </div>

            <div>
              <div className="label-caps">Transport</div>
              <div className="mt-2 text-[13px] font-semibold text-[#385b68]">
                {transportMode}
              </div>
            </div>

            <div>
              <div className="label-caps">Profile status</div>
              <div className="mt-2 text-[13px] font-semibold text-[#385b68]">
                {business.status}
              </div>
            </div>
          </div>

          <div className="mt-6 rounded-xl border border-[#eadcc6] bg-[#fbf7f0] p-4">
            <div className="flex items-center gap-2">
              <Clock3 size={14} className="text-[#8a6841]" />
              <span className="text-[11px] font-bold uppercase tracking-[0.12em] text-[#8a6841]">
                Applicability status
              </span>
            </div>

            <p className="mt-2 text-[12px] leading-5 text-[#7d6b56]">
              The current policy-change detail API does not expose a backend
              applicability determination. The business facts are shown above,
              but this dashboard does not infer legal applicability itself.
            </p>
          </div>
        </div>

        <div className="rounded-2xl border border-[#dce6e8] bg-white p-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="font-display text-[19px] font-semibold text-[#24495b]">
                Official source
              </h2>

              <p className="mt-1 text-[11px] text-[#8a9ba2]">
                Source metadata returned by the regulatory API
              </p>
            </div>

            <LibraryBig size={17} className="text-[#66808a]" />
          </div>

          <div className="mt-5 space-y-4">
            <div>
              <div className="label-caps">Source</div>
              <div className="mt-2 text-[13px] font-semibold text-[#385b68]">
                {document?.source.name ?? "Unavailable"}
              </div>
            </div>

            <div>
              <div className="label-caps">Document</div>
              <div className="mt-2 text-[13px] font-semibold text-[#385b68]">
                {document?.title ?? "Unavailable"}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="label-caps">Version</div>
                <div className="mt-2 text-[12px] font-medium text-[#506b76]">
                  {document?.version_label ?? "Not specified"}
                </div>
              </div>

              <div>
                <div className="label-caps">Publication</div>
                <div className="mt-2 text-[12px] font-medium text-[#506b76]">
                  {formatDate(document?.publication_date)}
                </div>
              </div>
            </div>

            {document?.url ? (
              <a
                href={document.url}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-2 rounded-xl border border-[#cfe0e2] bg-[#f8fbfb] px-4 py-3 text-[11px] font-bold text-[#3d7480] transition hover:bg-[#edf5f4]"
              >
                View official source
                <ArrowUpRight size={14} />
              </a>
            ) : (
              <div className="rounded-xl border border-[#e1e7e8] bg-[#f8fafb] px-4 py-3 text-[11px] font-medium text-[#819198]">
                Official source URL unavailable
              </div>
            )}
          </div>
        </div>
      </section>
    </div>
  );
}
