import {
  ArrowRight,
  CalendarDays,
  Search,
  X,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { Link } from "wouter";

import { getPolicyChangeDetail } from "../api/policyChanges";
import { DEMO_CONFIG } from "../config/demo";
import { ChangeKindPill } from "../components/StatusPill";
import { PageHeader } from "../components/PageHeader";
import type { PolicyChangeDetail } from "../types";

function formatDate(value: string | null) {
  if (!value) return "Date unavailable";

  return new Intl.DateTimeFormat("en", {
    year: "numeric",
    month: "short",
    day: "numeric",
  }).format(new Date(value));
}

export default function RegulatoryChanges() {
  const [change, setChange] = useState<PolicyChangeDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");

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
              : "Unable to load the regulatory change.",
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

  const matchesSearch = useMemo(() => {
    if (!change) return false;

    const oldClaim = change.old_claim?.text ?? "";
    const newClaim = change.new_claim?.text ?? "";

    const haystack = [
      change.change_type,
      change.summary,
      oldClaim,
      newClaim,
      change.old_claim?.section.section_number ?? "",
      change.new_claim?.section.section_number ?? "",
      change.old_claim?.section.document.title ?? "",
      change.new_claim?.section.document.title ?? "",
      change.old_claim?.section.document.source.name ?? "",
      change.new_claim?.section.document.source.name ?? "",
    ]
      .join(" ")
      .toLowerCase();

    return haystack.includes(search.trim().toLowerCase());
  }, [change, search]);

  if (loading) {
    return (
      <div className="page-enter mx-auto max-w-[1440px] px-5 py-10 md:px-8 lg:px-10">
        <div className="rounded-2xl border border-[#dce6e8] bg-white p-8 text-center text-[13px] text-[#7c9097]">
          Loading regulatory changes...
        </div>
      </div>
    );
  }

  if (error || !change) {
    return (
      <div className="page-enter mx-auto max-w-[1440px] px-5 py-10 md:px-8 lg:px-10">
        <div className="rounded-2xl border border-[#ead6d3] bg-[#fdf8f7] p-8">
          <h2 className="text-[14px] font-semibold text-[#8e5e59]">
            Regulatory change not found
          </h2>
          <p className="mt-2 text-[12px] leading-6 text-[#8b7774]">
            {error ?? "The requested regulatory change could not be loaded."}
          </p>
        </div>
      </div>
    );
  }

  const claim = change.new_claim ?? change.old_claim;
  const document = claim?.section.document;

  return (
    <div className="page-enter mx-auto max-w-[1440px] px-5 py-7 md:px-8 md:py-10 lg:px-10">
      <PageHeader
        eyebrow="Policy monitoring"
        title="Regulatory changes"
        description="Review the regulatory change returned by the policy-change API and follow it to the underlying evidence."
      />

      <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="relative">
          <Search
            size={15}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-[#9aabb0]"
          />

          <input
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search this change"
            className="h-10 w-full rounded-xl border border-[#dce6e8] bg-white pl-9 pr-9 text-[12px] text-[#345562] outline-none transition placeholder:text-[#a4b1b5] focus:border-[#9cc7c5] focus:ring-2 focus:ring-[#d9eeeb] sm:w-72"
          />

          {search && (
            <button
              onClick={() => setSearch("")}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-[#8da1a8]"
              aria-label="Clear search"
            >
              <X size={14} />
            </button>
          )}
        </div>

        <div className="text-[11px] text-[#9aa9ae]">
          Current demo record · API-backed
        </div>
      </div>

      {!matchesSearch ? (
        <div className="rounded-2xl border border-dashed border-[#d4e0e3] bg-white px-6 py-16 text-center">
          <div className="font-display text-xl font-semibold text-[#315565]">
            No matching change
          </div>
          <p className="mt-2 text-[12px] text-[#8b9ba1]">
            Try a different search term.
          </p>
        </div>
      ) : (
        <div className="overflow-hidden rounded-2xl border border-[#dce6e8] bg-white">
          <div className="hidden grid-cols-[minmax(0,1fr)_260px_180px_150px] gap-4 border-b border-[#e6edef] bg-[#fbfcfc] px-6 py-3 text-[10px] font-bold uppercase tracking-[0.17em] text-[#9aa9ae] md:grid">
            <div>Change</div>
            <div>Comparison</div>
            <div>Source</div>
            <div className="text-right">Effective</div>
          </div>

          <Link
            href={`/changes/${change.id}`}
            className="group grid gap-5 px-5 py-6 transition-colors hover:bg-[#fbfdfd] md:grid-cols-[minmax(0,1fr)_260px_180px_150px] md:items-center md:px-6"
          >
            <div className="min-w-0">
              <div className="mb-2 flex items-center gap-2">
                <ChangeKindPill
                  kind={
                    change.change_type === "MODIFIED" ||
                    change.change_type === "ADDED" ||
                    change.change_type === "REMOVED" ||
                    change.change_type === "REQUIRES_REVIEW"
                      ? change.change_type
                      : "REQUIRES_REVIEW"
                  }
                />

                {change.status && (
                  <span className="text-[10px] font-medium uppercase tracking-[0.1em] text-[#8a9ca2]">
                    {change.status}
                  </span>
                )}
              </div>

              <h2 className="text-[14px] font-semibold leading-5 text-[#294e5f] group-hover:text-[#1f6d74]">
                {change.summary}
              </h2>

              {claim && (
                <p className="mt-2 truncate text-[11px] text-[#8a9aa0]">
                  {claim.section.document.title}
                  <span className="px-1 text-[#c3cccf]">·</span>
                  Section {claim.section.section_number ?? "Unavailable"}
                </p>
              )}
            </div>

            <div className="space-y-2 text-[11px]">
              <div className="label-caps">Previous → Current</div>

              <div className="flex items-start gap-2 text-[12px] font-semibold text-[#31596b]">
                <span className="line-clamp-2 max-w-[105px] text-[#66808a]">
                  {change.old_claim?.text ?? "No prior claim"}
                </span>

                <ArrowRight
                  size={14}
                  className="mt-0.5 shrink-0 text-[#a1b3b8]"
                />

                <span className="line-clamp-2 max-w-[105px] text-[#277a72]">
                  {change.new_claim?.text ?? "No current claim"}
                </span>
              </div>
            </div>

            <div>
              <div className="label-caps">Source</div>

              <div className="mt-1.5 text-[11px] font-medium text-[#66808a]">
                {document?.source.name ?? "Source unavailable"}
              </div>
            </div>

            <div className="flex items-center gap-1.5 text-[11px] text-[#8a9aa0] md:justify-end">
              <CalendarDays size={13} />
              {formatDate(change.effective_date)}
            </div>
          </Link>
        </div>
      )}

      <div className="mt-5 flex flex-wrap items-center gap-x-5 gap-y-2 text-[11px] text-[#9aa9ae]">
        <span>
          Policy change ID:{" "}
          <span className="font-mono text-[#80939a]">{change.id}</span>
        </span>

        <span>
          Correspondence status:{" "}
          <span className="font-semibold text-[#8a6841]">
            {change.correspondence?.status ?? "Unavailable"}
          </span>
        </span>
      </div>
    </div>
  );
}
