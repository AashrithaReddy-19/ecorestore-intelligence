import type { AssessmentInput } from "../types";

export interface JsonValidationResult {
  value: AssessmentInput | null;
  error: string | null;
}

const NUMERIC_FIELDS = [
  "latitude",
  "longitude",
  "soil_organic_carbon_percent",
  "soil_ph",
  "soil_moisture_percent",
] as const;

export function validateAssessmentJson(text: string): JsonValidationResult {
  let parsed: unknown;
  try {
    parsed = JSON.parse(text);
  } catch (e) {
    return { value: null, error: e instanceof Error ? e.message : "Invalid JSON" };
  }

  if (typeof parsed !== "object" || parsed === null || Array.isArray(parsed)) {
    return { value: null, error: "JSON must be an object." };
  }

  const record = parsed as Record<string, unknown>;

  if (record.human_impact !== undefined && !Array.isArray(record.human_impact)) {
    return { value: null, error: "human_impact must be an array of strings." };
  }

  for (const field of NUMERIC_FIELDS) {
    const v = record[field];
    if (v !== undefined && v !== null && typeof v !== "number") {
      return { value: null, error: `${field} must be a number.` };
    }
  }

  if (record.soil_ph !== undefined && record.soil_ph !== null) {
    const ph = record.soil_ph as number;
    if (ph < 0 || ph > 14) {
      return { value: null, error: "soil_ph must be between 0 and 14." };
    }
  }

  return { value: { human_impact: [], ...record } as AssessmentInput, error: null };
}
