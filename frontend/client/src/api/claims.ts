import { apiRequest } from "./client";
import type {
  ClaimDetail,
  CompareRegulatoryVersionsResponse,
} from "../types";

export function getClaim(claimId: string) {
  return apiRequest<ClaimDetail>(`/claims/${claimId}`);
}

export function compareClaims(oldId: string, newId: string) {
  return apiRequest<CompareRegulatoryVersionsResponse>(
    `/claims/${oldId}/compare/${newId}`,
    { method: "POST" },
  );
}
