import { apiRequest } from "./client";
import type { PolicyChange, PolicyChangeDetail } from "../types";

export function getPolicyChange(policyChangeId: string) {
  return apiRequest<PolicyChange>(`/policy-changes/${policyChangeId}`);
}

export function getPolicyChangeDetail(policyChangeId: string) {
  return apiRequest<PolicyChangeDetail>(
    `/policy-changes/${policyChangeId}/detail`,
  );
}
