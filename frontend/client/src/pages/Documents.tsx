import {
  ArrowUpRight,
  CalendarDays,
  ExternalLink,
  FileText,
  Search,
  ShieldCheck,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { Link } from "wouter";

import { getPolicyChangeDetail } from "../api/policyChanges";
import { DEMO_CONFIG } from "../config/demo";
import { PageHeader } from "../components/PageHeader";
import StatusPill from "../components/StatusPill";
import type { ClaimDetail, DocumentDetail, PolicyChangeDetail } from "../types";

function formatDate(value: string | null) {
  if (!value) return "Unavailable";

  return new Intl.DateTimeFormat("en", {
    year: "numeric",
    month: "short",
    day: "numeric",
  }).format(new Date(value));
}

function collectDocuments(change: PolicyChangeDetail): DocumentDetail[] {
  const claims = [change.old_claim, change.new_claim].filter(
    (claim): claim is ClaimDetail => claim !== null,
  );

  const documents = claims.map((claim) => claim.section.document);

  return Array.from(
    new Map(
      documents.map((document) => [document.version_id, document]),
    ).values(),
  );
}

export function Documents() {
  const [change, setChange] = useState<PolicyChangeDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState("");

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
              : "Unable to load official documents.",
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

  const documents = useMemo(
    () => (change ? collectDocuments(change) : []),
    [change],
  );

  const filtered = useMemo(() => {
    const normalized = query.trim().toLowerCase();

    if (!normalized) return documents;

    return documents.filter((document) =>
      [
        document.title,
        document.document_type,
        document.version_label ?? "",
        document.source.name,
      ]
        .join(" ")
        .toLowerCase()
        .includes(normalized),
    );
  }, [documents, query]);

  if (loading) {
    return (
      <div className="page-enter mx-auto max-w-[1440px] px-5 py-10 md:px-8 lg:px-10">
        <div className="rounded-2xl border border-[#dce6e8] bg-white p-8 text-center text-[13px] text-[#7c9097]">
          Loading official documents...
        </div>
      </div>
    );
  }

  if (error || !change) {
    return (
      <div className="page-enter mx-auto max-w-[1440px] px-5 py-10 md:px-8 lg:px-10">
        <div className="rounded-2xl border border-[#ead6d3] bg-[#fdf8f7] p-8">
          <h2 className="text-[14px] font-semibold text-[#8e5e59]">
            Documents unavailable
          </h2>
          <p className="mt-2 text-[12px] leading-6 text-[#8b7774]">
            {error ?? "The official documents could not be loaded."}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="page-enter mx-auto max-w-[1440px] px-5 py-7 md:px-8 md:py-10 lg:px-10">
      <PageHeader
        eyebrow="Evidence library"
        title="Documents"
        description="Browse the official document versions that support the current regulatory comparison."
        actions={
          <div className="flex items-center gap-2 rounded-full border border-[#dbe6e7] bg-white px-3.5 py-2 text-[11px] font-medium text-[#66808a]">
            <ShieldCheck size={13} className="text-[#4c8b80]" />
            {documents.length} source versions
          </div>
        }
      />

      <div className="mb-6 flex items-center justify-between gap-3">
        <div className="relative">
          <Search
            size={15}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-[#9aabb0]"
          />

          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search documents"
            className="h-10 w-full rounded-xl border border-[#dce6e8] bg-white pl-9 pr-3 text-[12px] text-[#345562] outline-none placeholder:text-[#a4b1b5] focus:border-[#9cc7c5] focus:ring-2 focus:ring-[#d9eeeb] sm:w-72"
          />
        </div>

        <div className="hidden text-[11px] text-[#9aa9ae] md:block">
          Derived from the current policy-change evidence chain
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        {filtered.map((document) => (
          <Link
            key={document.version_id}
            href={`/documents/${document.id}`}
            className="group rounded-2xl border border-[#dce6e8] bg-white p-5 transition duration-200 hover:-translate-y-0.5 hover:border-[#bbd4d5] hover:shadow-[0_14px_28px_rgba(42,78,91,0.07)] md:p-6"
          >
            <div className="flex items-start justify-between gap-4">
              <div className="flex min-w-0 items-start gap-3">
                <div className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-[#edf3f4] text-[#4c7985]">
                  <FileText size={18} />
                </div>

                <div className="min-w-0">
                  <div className="mb-2 flex flex-wrap items-center gap-2">
                    <span className="text-[10px] font-bold uppercase tracking-[0.15em] text-[#72919a]">
                      {document.document_type}
                    </span>

                    {document.version_label && (
                      <span className="rounded-full border border-[#cfe4df] bg-[#eef7f4] px-2 py-0.5 text-[9px] font-semibold uppercase tracking-[0.12em] text-[#37716f]">
                        {document.version_label}
                      </span>
                    )}
                  </div>

                  <h2 className="max-w-lg text-[14px] font-semibold leading-5 text-[#2a5263] group-hover:text-[#1d6b71]">
                    {document.title}
                  </h2>
                </div>
              </div>

              <ArrowUpRight
                size={16}
                className="shrink-0 text-[#9bb0b5] transition group-hover:text-[#2f7b7d]"
              />
            </div>

            <div className="mt-6 grid grid-cols-2 gap-4 border-t border-[#edf1f2] pt-4 sm:grid-cols-4">
              <div>
                <div className="label-caps">Source</div>
                <div className="mt-1.5 text-[11px] font-medium text-[#66808a]">
                  {document.source.name}
                </div>
              </div>

              <div>
                <div className="label-caps">Published</div>
                <div className="mt-1.5 flex items-center gap-1 text-[11px] font-medium text-[#66808a]">
                  <CalendarDays size={12} />
                  {formatDate(document.publication_date)}
                </div>
              </div>

              <div>
                <div className="label-caps">Effective</div>
                <div className="mt-1.5 text-[11px] font-medium text-[#66808a]">
                  {formatDate(document.effective_date)}
                </div>
              </div>

              <div>
                <div className="label-caps">Authority</div>
                <div className="mt-1.5 text-[11px] font-semibold text-[#37716f]">
                  {document.source.authority_tier}
                </div>
              </div>
            </div>
          </Link>
        ))}
      </div>

      {!filtered.length && (
        <div className="mt-4 rounded-2xl border border-dashed border-[#d4e0e3] bg-white px-6 py-16 text-center text-[12px] text-[#82949b]">
          No documents match your search.
        </div>
      )}

      <div className="mt-5 text-[11px] text-[#9aa9ae]">
        Documents shown here are the official source versions connected to
        the loaded policy change.
      </div>
    </div>
  );
}

export function DocumentDetail({ id }: { id?: string }) {
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
              : "Unable to load the document.",
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
      <div className="page-enter mx-auto max-w-[1200px] px-5 py-10 md:px-8 lg:px-10">
        <div className="rounded-2xl border border-[#dce6e8] bg-white p-8 text-center text-[13px] text-[#7c9097]">
          Loading official document...
        </div>
      </div>
    );
  }

  if (error || !change) {
    return (
      <div className="page-enter mx-auto max-w-[1200px] px-5 py-10 md:px-8 lg:px-10">
        <div className="rounded-2xl border border-[#ead6d3] bg-[#fdf8f7] p-8">
          <h2 className="text-[14px] font-semibold text-[#8e5e59]">
            Document unavailable
          </h2>
          <p className="mt-2 text-[12px] leading-6 text-[#8b7774]">
            {error ?? "The requested document could not be loaded."}
          </p>
        </div>
      </div>
    );
  }

  const documents = collectDocuments(change);
  const document = documents.find((item) => item.id === id);

  if (!document) {
    return (
      <div className="page-enter mx-auto max-w-[1200px] px-5 py-10 md:px-8 lg:px-10">
        <PageHeader
          backHref="/documents"
          backLabel="Document library"
          eyebrow="Official document"
          title="Document not found"
          description="This document is not part of the current policy-change evidence chain."
        />

        <div className="rounded-2xl border border-dashed border-[#d4e0e3] bg-white p-8 text-[12px] text-[#82949b]">
          No matching document was returned by the policy-change API.
        </div>
      </div>
    );
  }

  const relatedClaims = [change.old_claim, change.new_claim].filter(
    (claim): claim is ClaimDetail =>
      claim !== null && claim.section.document.id === document.id,
  );

  return (
    <div className="page-enter mx-auto max-w-[1200px] px-5 py-7 md:px-8 md:py-10 lg:px-10">
      <PageHeader
        backHref="/documents"
        backLabel="Document library"
        eyebrow="Official document"
        title={document.title}
        description="Document metadata and the regulatory claims connected to this source version."
        actions={
          document.url ? (
            <a
              href={document.url}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-2 rounded-xl bg-[#245f68] px-4 py-2.5 text-[11px] font-semibold text-white transition hover:bg-[#1e5159]"
            >
              <ExternalLink size={13} />
              View official source
            </a>
          ) : (
            <span className="rounded-full border border-[#eadcc6] bg-[#f6f1e8] px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.12em] text-[#8a6841]">
              Official source URL unavailable
            </span>
          )
        }
      />

      <div className="grid gap-5 lg:grid-cols-[1fr_320px]">
        <div className="space-y-5">
          <section className="rounded-2xl border border-[#dce6e8] bg-white p-6">
            <div className="label-caps">Document metadata</div>

            <div className="mt-5 grid gap-5 sm:grid-cols-2">
              <div>
                <div className="label-caps">Issuing source</div>
                <div className="mt-2 text-[13px] font-semibold text-[#3e6271]">
                  {document.source.name}
                </div>
              </div>

              <div>
                <div className="label-caps">Document type</div>
                <div className="mt-2 text-[13px] font-semibold text-[#3e6271]">
                  {document.document_type}
                </div>
              </div>

              <div>
                <div className="label-caps">Version</div>
                <div className="mt-2 text-[13px] font-semibold text-[#3e6271]">
                  {document.version_label ?? "Version unavailable"}
                </div>
              </div>

              <div>
                <div className="label-caps">Publication date</div>
                <div className="mt-2 text-[13px] font-semibold text-[#3e6271]">
                  {formatDate(document.publication_date)}
                </div>
              </div>

              <div>
                <div className="label-caps">Effective date</div>
                <div className="mt-2 text-[13px] font-semibold text-[#3e6271]">
                  {formatDate(document.effective_date)}
                </div>
              </div>

              <div>
                <div className="label-caps">Authority tier</div>
                <div className="mt-2 text-[13px] font-semibold text-[#3e6271]">
                  {document.source.authority_tier}
                </div>
              </div>
            </div>
          </section>

          <section className="rounded-2xl border border-[#dce6e8] bg-white p-6">
            <div className="label-caps">Connected claims</div>

            <h2 className="mt-2 font-display text-[21px] font-semibold text-[#274d5d]">
              Regulatory evidence
            </h2>

            <div className="mt-5 divide-y divide-[#edf1f2]">
              {relatedClaims.map((claim) => (
                <div
                  key={claim.id}
                  className="py-5 first:pt-0 last:pb-0"
                >
                  <div className="text-[11px] font-bold uppercase tracking-[0.14em] text-[#53848a]">
                    Section {claim.section.section_number ?? "Unavailable"}
                    {claim.section.page_start !== null && (
                      <>
                        <span className="px-1 text-[#becacc]">·</span>
                        Page {claim.section.page_start}
                      </>
                    )}
                  </div>

                  <p className="mt-3 text-[13px] leading-7 text-[#617b83]">
                    {claim.text}
                  </p>

                  {claim.evidence.length > 0 && (
                    <div className="mt-4 rounded-xl border border-[#e1eaeb] bg-[#f8fbfb] p-4">
                      <div className="label-caps">Evidence</div>

                      {claim.evidence.map((evidence) => (
                        <div
                          key={evidence.id}
                          className="mt-3 border-l-2 border-[#7aa39f] pl-3 text-[12px] leading-6 text-[#58747d]"
                        >
                          “{evidence.quote}”
                          {evidence.page !== null && (
                            <div className="mt-1 text-[10px] text-[#8da0a5]">
                              Page {evidence.page}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </section>
        </div>

        <aside className="h-fit rounded-2xl border border-[#dce6e8] bg-[#f8fbfb] p-5">
          <div className="label-caps">Source record</div>

          <div className="mt-4 space-y-4">
            <div>
              <div className="label-caps">Source</div>
              <div className="mt-1.5 text-[12px] font-semibold text-[#3b6270]">
                {document.source.name}
              </div>
            </div>

            <div>
              <div className="label-caps">Institution type</div>
              <div className="mt-1.5 text-[12px] font-semibold text-[#3b6270]">
                {document.source.institution_type ?? "Unavailable"}
              </div>
            </div>

            <div>
              <div className="label-caps">Document ID</div>
              <div className="mt-1.5 break-all font-mono text-[10px] text-[#83979d]">
                {document.id}
              </div>
            </div>

            <div>
              <div className="label-caps">Version ID</div>
              <div className="mt-1.5 break-all font-mono text-[10px] text-[#83979d]">
                {document.version_id}
              </div>
            </div>
          </div>

          {document.url && (
            <a
              href={document.url}
              target="_blank"
              rel="noreferrer"
              className="mt-6 flex items-center justify-center gap-2 rounded-xl border border-[#cfe0e1] bg-white px-4 py-3 text-[11px] font-semibold text-[#39717a] transition hover:bg-[#f0f6f6]"
            >
              <ExternalLink size={13} />
              Open official source
            </a>
          )}
        </aside>
      </div>
    </div>
  );
}
