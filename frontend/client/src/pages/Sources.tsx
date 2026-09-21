import { Activity, Check, ExternalLink } from "lucide-react";
import { useEffect, useState } from "react";

import { getBusinessProfile } from "../api/businessProfiles";
import { DEMO_CONFIG } from "../config/demo";
import { PageHeader } from "../components/PageHeader";
import type { BusinessProfile } from "../types";

export default function Sources() {
  const [profile, setProfile] = useState<BusinessProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    getBusinessProfile(DEMO_CONFIG.businessProfileId)
      .then((result) => {
        if (!cancelled) {
          setProfile(result);
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setError(
            err instanceof Error
              ? err.message
              : "Unable to load tracked sources.",
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
          Loading tracked sources...
        </div>
      </div>
    );
  }

  if (error || !profile) {
    return (
      <div className="page-enter mx-auto max-w-[1200px] px-5 py-10 md:px-8 lg:px-10">
        <div className="rounded-2xl border border-[#ead6d3] bg-[#fdf8f7] p-8">
          <h2 className="text-[14px] font-semibold text-[#8e5e59]">
            Unable to load sources
          </h2>
          <p className="mt-2 text-[12px] leading-6 text-[#8b7774]">
            {error ?? "The business profile could not be loaded."}
          </p>
        </div>
      </div>
    );
  }

  const sources = profile.tracked_sources;

  return (
    <div className="page-enter mx-auto max-w-[1200px] px-5 py-7 md:px-8 md:py-10 lg:px-10">
      <PageHeader
        eyebrow="Source monitoring"
        title="Sources"
        description="Authoritative institutions tracked by the selected business profile."
        actions={
          <div className="flex items-center gap-2 rounded-full border border-[#dbe6e7] bg-white px-3.5 py-2 text-[11px] font-medium text-[#66808a]">
            <Activity size={13} className="text-[#4c8b80]" />
            {sources.length} tracked {sources.length === 1 ? "source" : "sources"}
          </div>
        }
      />

      {sources.length > 0 ? (
        <div className="grid gap-4 sm:grid-cols-2">
          {sources.map((source) => (
            <article
              key={source.id}
              className="rounded-2xl border border-[#dce6e8] bg-white p-5 transition hover:border-[#bfd5d7] hover:shadow-[0_12px_24px_rgba(42,78,91,0.05)] md:p-6"
            >
              <div className="flex items-start gap-3">
                <div className="grid h-11 w-11 shrink-0 place-items-center rounded-xl bg-[#e9f1f2] text-[#477582]">
                  <Check size={17} />
                </div>

                <div className="min-w-0">
                  <h2 className="text-[14px] font-semibold text-[#2d5464]">
                    {source.name}
                  </h2>

                  <div className="mt-2 flex flex-wrap items-center gap-2">
                    <span className="rounded-full border border-[#cfe1e2] bg-[#f0f6f6] px-2 py-0.5 text-[9px] font-bold uppercase tracking-[0.13em] text-[#4d7e83]">
                      {source.authority_tier}
                    </span>

                    {source.institution_type && (
                      <span className="text-[10px] font-medium uppercase tracking-[0.1em] text-[#8b9da3]">
                        {source.institution_type}
                      </span>
                    )}
                  </div>
                </div>
              </div>

              <div className="mt-5 border-t border-[#edf1f2] pt-4">
                <div className="label-caps">Base URL</div>

                {source.base_url ? (
                  <a
                    href={source.base_url}
                    target="_blank"
                    rel="noreferrer"
                    className="mt-2 inline-flex max-w-full items-center gap-1.5 break-all text-[11px] font-medium text-[#39757b] hover:text-[#245f68]"
                  >
                    {source.base_url}
                    <ExternalLink size={12} className="shrink-0" />
                  </a>
                ) : (
                  <div className="mt-2 text-[11px] text-[#89999f]">
                    Source URL unavailable
                  </div>
                )}
              </div>

              <div className="mt-5 rounded-xl border border-[#e2ebec] bg-[#f8fbfb] px-3.5 py-3 text-[11px] leading-5 text-[#7b9097]">
                This source relationship is returned by the business-profile
                API. The frontend does not modify tracking configuration.
              </div>
            </article>
          ))}
        </div>
      ) : (
        <div className="rounded-2xl border border-dashed border-[#d4e0e3] bg-white px-6 py-16 text-center">
          <div className="font-display text-xl font-semibold text-[#315565]">
            No tracked sources
          </div>
          <p className="mt-2 text-[12px] text-[#82949b]">
            The selected business profile does not currently have any tracked
            source relationships.
          </p>
        </div>
      )}

      <div className="mt-5 text-[11px] text-[#99a8ad]">
        Business profile: {profile.name}
      </div>
    </div>
  );
}
