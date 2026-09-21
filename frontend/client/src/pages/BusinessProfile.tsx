import { useEffect, useMemo, useState } from "react";
import { Check, MapPin, Ship, UserRound } from "lucide-react";

import { getBusinessProfile } from "../api/businessProfiles";
import { DEMO_CONFIG } from "../config/demo";
import { PageHeader } from "../components/PageHeader";
import type { BusinessProfile } from "../types";

function formatEntityType(value: string) {
  return value.replaceAll("_", " ");
}

export default function BusinessProfilePage() {
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
              : "Unable to load the business profile.",
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

  const activity = useMemo(
    () =>
      profile?.entities.find(
        (entity) => entity.entity_type.toUpperCase() === "ACTIVITY",
      ),
    [profile],
  );

  const transportMode = useMemo(
    () =>
      profile?.entities.find(
        (entity) =>
          entity.entity_type.toUpperCase() === "TRANSPORT_MODE",
      ),
    [profile],
  );

  if (loading) {
    return (
      <div className="page-enter mx-auto max-w-[1100px] px-5 py-10 md:px-8 lg:px-10">
        <div className="rounded-2xl border border-[#dce6e8] bg-white p-8 text-center text-[13px] text-[#7c9097]">
          Loading business profile...
        </div>
      </div>
    );
  }

  if (error || !profile) {
    return (
      <div className="page-enter mx-auto max-w-[1100px] px-5 py-10 md:px-8 lg:px-10">
        <div className="rounded-2xl border border-[#ead6d3] bg-[#fdf8f7] p-8">
          <h2 className="text-[14px] font-semibold text-[#8e5e59]">
            Business profile not found
          </h2>
          <p className="mt-2 text-[12px] leading-6 text-[#8b7774]">
            {error ?? "The requested business profile could not be loaded."}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="page-enter mx-auto max-w-[1100px] px-5 py-7 md:px-8 md:py-10 lg:px-10">
      <PageHeader
        eyebrow="Applicability context"
        title="Business profile"
        description="Business facts are displayed from the backend profile. They provide context for regulatory applicability but are not interpreted by the frontend."
      />

      <div className="grid gap-5 lg:grid-cols-[1fr_320px]">
        <section className="rounded-2xl border border-[#dce6e8] bg-white p-6 md:p-7">
          <div className="flex items-start gap-4 border-b border-[#e7edef] pb-6">
            <div className="grid h-14 w-14 place-items-center rounded-2xl bg-[#e6f0f1] text-[#39747a]">
              <UserRound size={23} />
            </div>

            <div>
              <div className="label-caps">Business</div>

              <h2 className="mt-1.5 font-display text-[27px] font-semibold tracking-[-0.035em] text-[#244b5b]">
                {profile.name}
              </h2>

              {profile.description && (
                <div className="mt-2 text-[11px] leading-5 text-[#84979d]">
                  {profile.description}
                </div>
              )}

              <div className="mt-2 flex items-center gap-1.5 text-[11px] text-[#8a9ca2]">
                <MapPin size={12} />
                Backend profile
              </div>
            </div>
          </div>

          <div className="mt-6 grid gap-6 sm:grid-cols-3">
            <div>
              <div className="label-caps">Activity</div>
              <div className="mt-2 text-[14px] font-semibold capitalize text-[#3d6270]">
                {activity?.name ?? "Not specified"}
              </div>
              <p className="mt-1 text-[11px] text-[#8a9aa0]">
                Business activity recorded by the backend
              </p>
            </div>

            <div>
              <div className="label-caps">Transport mode</div>
              <div className="mt-2 flex items-center gap-2 text-[14px] font-semibold capitalize text-[#3d6270]">
                <Ship size={16} className="text-[#6a9699]" />
                {transportMode?.name ?? "Not specified"}
              </div>
              <p className="mt-1 text-[11px] text-[#8a9aa0]">
                Business fact available to applicability logic
              </p>
            </div>

            <div>
              <div className="label-caps">Profile status</div>
              <div className="mt-2 text-[14px] font-semibold text-[#3d6270]">
                {profile.status}
              </div>
              <p className="mt-1 text-[11px] text-[#8a9aa0]">
                Status returned by the backend
              </p>
            </div>
          </div>

          <div className="mt-7 rounded-xl border border-[#dce6e8] bg-[#f8fbfb] px-4 py-3 text-[11px] leading-5 text-[#6f858c]">
            The frontend displays these facts but does not determine whether a
            regulatory requirement applies.
          </div>
        </section>

        <aside className="rounded-2xl border border-[#dce6e8] bg-[#f8fbfb] p-6">
          <div className="label-caps">Tracked sources</div>

          <h2 className="mt-2 font-display text-xl font-semibold text-[#2b5261]">
            {profile.tracked_sources.length} authorities in scope
          </h2>

          <div className="mt-5 space-y-3">
            {profile.tracked_sources.length > 0 ? (
              profile.tracked_sources.map((source) => (
                <div
                  key={source.id}
                  className="rounded-xl border border-[#e2ebec] bg-white px-3.5 py-3"
                >
                  <div className="flex items-center gap-3">
                    <span className="grid h-7 w-7 place-items-center rounded-lg bg-[#edf5f4] text-[#4b827c]">
                      <Check size={14} />
                    </span>

                    <span className="text-[12px] font-medium text-[#55727b]">
                      {source.name}
                    </span>
                  </div>

                  <div className="mt-2 pl-10 text-[9px] font-semibold uppercase tracking-[0.12em] text-[#8aa0a6]">
                    {source.authority_tier}
                    {source.institution_type
                      ? ` · ${source.institution_type}`
                      : ""}
                  </div>
                </div>
              ))
            ) : (
              <div className="text-[11px] text-[#87999f]">
                No tracked sources returned.
              </div>
            )}
          </div>

          <p className="mt-5 text-[11px] leading-5 text-[#87999f]">
            Source relationships are displayed from the business-profile API.
          </p>
        </aside>
      </div>

      <div className="mt-5 rounded-2xl border border-[#dce6e8] bg-white p-6">
        <div className="label-caps">Why this matters</div>

        <div className="mt-3 max-w-3xl text-[13px] leading-7 text-[#70858d]">
          Business facts remain separate from regulatory claims and evidence.
          When the backend exposes an applicability result, that result can
          be displayed alongside the facts that support it.
        </div>
      </div>

      <div className="mt-5 text-[11px] text-[#9aa9ae]">
        Profile ID: {profile.id}
      </div>
    </div>
  );
}
