import { apiRequest } from "./client";
import type { BusinessProfile } from "../types";

export function getBusinessProfile(profileId: string) {
  return apiRequest<BusinessProfile>(
    `/business-profiles/${profileId}`,
  );
}
