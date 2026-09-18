import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/client";
import AssessmentForm from "../components/AssessmentForm";
import MapPanel from "../components/MapPanel";
import { useAssessment } from "../context/AssessmentContext";
import { SUNDARBANS_SAMPLE } from "../data/sundarbansSample";
import type { AssessmentInput } from "../types";
import { validateAssessmentJson } from "../utils/validateAssessmentJson";

type Tab = "form" | "json";

export default function AssessmentPage() {
  const [tab, setTab] = useState<Tab>("form");
  const [value, setValue] = useState<AssessmentInput>(SUNDARBANS_SAMPLE);
  const [jsonText, setJsonText] = useState(JSON.stringify(SUNDARBANS_SAMPLE, null, 2));
  const [jsonError, setJsonError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { setAssessment } = useAssessment();
  const navigate = useNavigate();

  const validateJson = (text: string): AssessmentInput | null => {
    const { value: parsedValue, error } = validateAssessmentJson(text);
    setJsonError(error);
    return parsedValue;
  };

  const loadSample = () => {
    setValue(SUNDARBANS_SAMPLE);
    setJsonText(JSON.stringify(SUNDARBANS_SAMPLE, null, 2));
    setJsonError(null);
  };

  const submit = async () => {
    setError(null);
    let payload: AssessmentInput | null = value;
    if (tab === "json") {
      payload = validateJson(jsonText);
      if (!payload) return;
    }
    setSubmitting(true);
    try {
      const result = await api.createAssessment(payload);
      setAssessment(result);
      navigate("/plan");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to submit assessment");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-eco-900">Environmental Assessment</h1>
        <p className="text-slate-600 mt-1">
          Submit structured ecosystem data to generate an evidence-grounded biodiversity risk
          assessment and ranked recovery plan.
        </p>
      </div>

      <div className="flex items-center justify-between">
        <div className="inline-flex rounded-lg border border-slate-200 bg-white p-1">
          <button
            type="button"
            className={`px-4 py-1.5 text-sm rounded-md ${tab === "form" ? "bg-eco-600 text-white" : "text-slate-600"}`}
            onClick={() => setTab("form")}
          >
            Form
          </button>
          <button
            type="button"
            className={`px-4 py-1.5 text-sm rounded-md ${tab === "json" ? "bg-eco-600 text-white" : "text-slate-600"}`}
            onClick={() => setTab("json")}
          >
            JSON input
          </button>
        </div>
        <button
          type="button"
          onClick={loadSample}
          className="text-sm text-eco-700 hover:underline"
        >
          Load Sundarbans sample scenario
        </button>
      </div>

      {value.latitude != null && value.longitude != null && (
        <MapPanel latitude={value.latitude} longitude={value.longitude} label={value.location_name ?? undefined} />
      )}

      <div className="bg-white rounded-xl border border-slate-200 p-6">
        {tab === "form" ? (
          <AssessmentForm value={value} onChange={setValue} />
        ) : (
          <div>
            <textarea
              aria-label="Assessment JSON input"
              className="w-full h-80 font-mono text-xs rounded-md border border-slate-300 p-3 focus:border-eco-500 focus:outline-none focus:ring-1 focus:ring-eco-500"
              value={jsonText}
              onChange={(e) => {
                setJsonText(e.target.value);
                validateJson(e.target.value);
              }}
            />
            {jsonError && (
              <p role="alert" className="mt-2 text-sm text-red-600">
                Invalid JSON: {jsonError}
              </p>
            )}
          </div>
        )}
      </div>

      {error && <p className="text-sm text-red-600">{error}</p>}

      <button
        type="button"
        onClick={submit}
        disabled={submitting || (tab === "json" && !!jsonError)}
        className="w-full md:w-auto px-6 py-2.5 rounded-lg bg-eco-600 text-white font-medium hover:bg-eco-700 disabled:opacity-50"
      >
        {submitting ? "Analyzing..." : "Generate Recovery Plan"}
      </button>
    </div>
  );
}
