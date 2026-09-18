import { useState } from "react";
import { api } from "../api/client";
import { useAssessment } from "../context/AssessmentContext";
import type { MRVTracker } from "../types";

interface MetricFormState {
  soil_organic_carbon_percent: string;
  soil_moisture_percent: string;
  species_richness_index: string;
  habitat_connectivity_index: string;
  pollution_risk_index: string;
  notes: string;
}

const EMPTY_METRICS: MetricFormState = {
  soil_organic_carbon_percent: "",
  soil_moisture_percent: "",
  species_richness_index: "",
  habitat_connectivity_index: "",
  pollution_risk_index: "",
  notes: "",
};

function toNumberOrNull(s: string): number | null {
  if (s.trim() === "") return null;
  const n = Number(s);
  return Number.isNaN(n) ? null : n;
}

function MetricInputs({
  value,
  onChange,
}: {
  value: MetricFormState;
  onChange: (v: MetricFormState) => void;
}) {
  const inputClass =
    "mt-1 w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm focus:border-eco-500 focus:outline-none focus:ring-1 focus:ring-eco-500";
  const set = (k: keyof MetricFormState, v: string) => onChange({ ...value, [k]: v });
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
      <label className="text-xs font-medium text-slate-600">
        Soil organic carbon (%)
        <input
          className={inputClass}
          type="number"
          value={value.soil_organic_carbon_percent}
          onChange={(e) => set("soil_organic_carbon_percent", e.target.value)}
        />
      </label>
      <label className="text-xs font-medium text-slate-600">
        Soil moisture (%)
        <input
          className={inputClass}
          type="number"
          value={value.soil_moisture_percent}
          onChange={(e) => set("soil_moisture_percent", e.target.value)}
        />
      </label>
      <label className="text-xs font-medium text-slate-600">
        Species richness index
        <input
          className={inputClass}
          type="number"
          value={value.species_richness_index}
          onChange={(e) => set("species_richness_index", e.target.value)}
        />
      </label>
      <label className="text-xs font-medium text-slate-600">
        Habitat connectivity index
        <input
          className={inputClass}
          type="number"
          value={value.habitat_connectivity_index}
          onChange={(e) => set("habitat_connectivity_index", e.target.value)}
        />
      </label>
      <label className="text-xs font-medium text-slate-600 col-span-2 md:col-span-1">
        Pollution risk index (lower is better)
        <input
          className={inputClass}
          type="number"
          value={value.pollution_risk_index}
          onChange={(e) => set("pollution_risk_index", e.target.value)}
        />
      </label>
      <label className="text-xs font-medium text-slate-600 col-span-2 md:col-span-3">
        Notes
        <input className={inputClass} value={value.notes} onChange={(e) => set("notes", e.target.value)} />
      </label>
    </div>
  );
}

const TREND_STYLE: Record<string, string> = {
  improved: "text-eco-700 bg-eco-50 border-eco-200",
  declined: "text-red-700 bg-red-50 border-red-200",
  no_change: "text-slate-600 bg-slate-50 border-slate-200",
  insufficient_data: "text-slate-400 bg-slate-50 border-slate-200",
};

export default function MRVTrackerPage() {
  const { assessment } = useAssessment();
  const [assessmentId, setAssessmentId] = useState(assessment?.assessment_id ?? "");
  const [baselineForm, setBaselineForm] = useState<MetricFormState>(EMPTY_METRICS);
  const [observationForm, setObservationForm] = useState<MetricFormState>(EMPTY_METRICS);
  const [baselineId, setBaselineId] = useState<string | null>(null);
  const [tracker, setTracker] = useState<MRVTracker | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const refreshTracker = async (id: string) => {
    try {
      const t = await api.getMrvTracker(id);
      setTracker(t);
    } catch {
      setTracker(null);
    }
  };

  const saveBaseline = async () => {
    if (!assessmentId) {
      setMessage("Enter an assessment ID first (from the Recovery Plan page).");
      return;
    }
    try {
      const res = await api.createBaseline({
        assessment_id: assessmentId,
        soil_organic_carbon_percent: toNumberOrNull(baselineForm.soil_organic_carbon_percent),
        soil_moisture_percent: toNumberOrNull(baselineForm.soil_moisture_percent),
        species_richness_index: toNumberOrNull(baselineForm.species_richness_index),
        habitat_connectivity_index: toNumberOrNull(baselineForm.habitat_connectivity_index),
        pollution_risk_index: toNumberOrNull(baselineForm.pollution_risk_index),
        notes: baselineForm.notes || null,
      });
      setBaselineId(res.baseline_id);
      setMessage("Baseline saved.");
      await refreshTracker(assessmentId);
    } catch (e) {
      setMessage(e instanceof Error ? e.message : "Failed to save baseline");
    }
  };

  const addObservation = async () => {
    if (!baselineId) {
      setMessage("Save a baseline first.");
      return;
    }
    try {
      await api.addObservation({
        baseline_id: baselineId,
        soil_organic_carbon_percent: toNumberOrNull(observationForm.soil_organic_carbon_percent),
        soil_moisture_percent: toNumberOrNull(observationForm.soil_moisture_percent),
        species_richness_index: toNumberOrNull(observationForm.species_richness_index),
        habitat_connectivity_index: toNumberOrNull(observationForm.habitat_connectivity_index),
        pollution_risk_index: toNumberOrNull(observationForm.pollution_risk_index),
        notes: observationForm.notes || null,
      });
      setObservationForm(EMPTY_METRICS);
      setMessage("Follow-up observation added.");
      await refreshTracker(assessmentId);
    } catch (e) {
      setMessage(e instanceof Error ? e.message : "Failed to add observation");
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-eco-900">MRV Tracker</h1>
        <p className="text-slate-600 mt-1">
          Save a baseline ecosystem assessment, then add follow-up observations over time. Real
          improvement is only reported once follow-up values are actually entered.
        </p>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-6 space-y-4">
        <label className="block text-sm">
          <span className="font-medium text-slate-700">Assessment ID</span>
          <input
            className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm font-mono"
            value={assessmentId}
            onChange={(e) => setAssessmentId(e.target.value)}
            placeholder="paste assessment_id from Recovery Plan"
          />
        </label>
        {assessment && (
          <p className="text-xs text-slate-500">
            Currently loaded assessment: {assessment.assessment_id} ({assessment.biodiversity_risk_level} risk)
          </p>
        )}
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-6 space-y-3">
        <h2 className="font-semibold text-eco-900">1. Baseline</h2>
        <MetricInputs value={baselineForm} onChange={setBaselineForm} />
        <button
          type="button"
          onClick={saveBaseline}
          className="px-4 py-2 rounded-md bg-eco-600 text-white text-sm font-medium hover:bg-eco-700"
        >
          Save baseline
        </button>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-6 space-y-3">
        <h2 className="font-semibold text-eco-900">2. Add follow-up observation</h2>
        <MetricInputs value={observationForm} onChange={setObservationForm} />
        <button
          type="button"
          onClick={addObservation}
          disabled={!baselineId}
          className="px-4 py-2 rounded-md bg-eco-600 text-white text-sm font-medium hover:bg-eco-700 disabled:opacity-50"
        >
          Add observation
        </button>
      </div>

      {message && <p className="text-sm text-eco-700">{message}</p>}

      {tracker && (
        <div className="bg-white rounded-xl border border-slate-200 p-6 space-y-4">
          <h2 className="font-semibold text-eco-900">3. Baseline vs. follow-up comparison</h2>
          <p className="text-sm text-slate-600">{tracker.summary}</p>
          <table className="w-full text-sm border-collapse">
            <thead>
              <tr className="text-left text-xs uppercase text-slate-500 border-b border-slate-200">
                <th className="py-2">Metric</th>
                <th className="py-2">Baseline</th>
                <th className="py-2">Latest</th>
                <th className="py-2">Delta</th>
                <th className="py-2">Trend</th>
              </tr>
            </thead>
            <tbody>
              {tracker.comparisons.map((c) => (
                <tr key={c.metric} className="border-b border-slate-100">
                  <td className="py-2 font-medium">{c.metric}</td>
                  <td className="py-2">{c.baseline_value ?? "—"}</td>
                  <td className="py-2">{c.latest_value ?? "—"}</td>
                  <td className="py-2">{c.delta ?? "—"}</td>
                  <td className="py-2">
                    <span className={`px-2 py-0.5 rounded-full text-xs border ${TREND_STYLE[c.trend]}`}>
                      {c.trend.replace("_", " ")}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
