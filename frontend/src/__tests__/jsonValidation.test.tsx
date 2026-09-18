import { describe, expect, it } from "vitest";
import { SUNDARBANS_SAMPLE } from "../data/sundarbansSample";
import { validateAssessmentJson } from "../utils/validateAssessmentJson";

describe("validateAssessmentJson", () => {
  it("accepts the Sundarbans sample scenario", () => {
    const result = validateAssessmentJson(JSON.stringify(SUNDARBANS_SAMPLE));
    expect(result.error).toBeNull();
    expect(result.value?.ecosystem_type).toBe("mangrove");
  });

  it("rejects malformed JSON with a parse error", () => {
    const result = validateAssessmentJson("{ not valid json ");
    expect(result.value).toBeNull();
    expect(result.error).toBeTruthy();
  });

  it("rejects a JSON array as the top-level value", () => {
    const result = validateAssessmentJson("[1, 2, 3]");
    expect(result.value).toBeNull();
    expect(result.error).toMatch(/object/i);
  });

  it("rejects human_impact that is not an array", () => {
    const result = validateAssessmentJson(JSON.stringify({ human_impact: "pollution" }));
    expect(result.value).toBeNull();
    expect(result.error).toMatch(/human_impact/i);
  });

  it("rejects out-of-range soil_ph", () => {
    const result = validateAssessmentJson(JSON.stringify({ soil_ph: 25 }));
    expect(result.value).toBeNull();
    expect(result.error).toMatch(/soil_ph/i);
  });

  it("rejects non-numeric latitude", () => {
    const result = validateAssessmentJson(JSON.stringify({ latitude: "north" }));
    expect(result.value).toBeNull();
    expect(result.error).toMatch(/latitude/i);
  });

  it("defaults human_impact to an empty array when omitted", () => {
    const result = validateAssessmentJson(JSON.stringify({ ecosystem_type: "forest" }));
    expect(result.error).toBeNull();
    expect(result.value?.human_impact).toEqual([]);
  });
});
