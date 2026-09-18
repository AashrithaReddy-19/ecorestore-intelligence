import type { Recommendation } from "../types";
import EvidenceList from "./EvidenceList";

const HORIZON_LABEL: Record<Recommendation["time_horizon"], string> = {
  short: "Short-term",
  medium: "Medium-term",
  long: "Long-term",
};

const DIRECTION_ICON: Record<string, string> = {
  increase: "▲",
  decrease: "▼",
  stabilise: "●",
};

export default function RecommendationCard({ rec }: { rec: Recommendation }) {
  return (
    <article
      className="rounded-xl border border-slate-200 bg-white shadow-sm p-5 space-y-4"
      data-testid="recommendation-card"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-3">
          <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-eco-600 text-white font-semibold">
            {rec.priority}
          </span>
          <h3 className="text-lg font-semibold text-eco-900">{rec.action}</h3>
        </div>
        <span className="text-xs font-medium px-2 py-1 rounded-full bg-eco-50 text-eco-700 border border-eco-200 shrink-0">
          {HORIZON_LABEL[rec.time_horizon]}
        </span>
      </div>

      <div>
        <h4 className="text-xs uppercase tracking-wide text-slate-500 font-semibold mb-1">
          Why it works
        </h4>
        <p className="text-sm text-slate-700">{rec.scientific_reasoning}</p>
      </div>

      <div>
        <h4 className="text-xs uppercase tracking-wide text-slate-500 font-semibold mb-1">
          Impacted metrics
        </h4>
        <ul className="space-y-1">
          {rec.impacted_metrics.map((m) => (
            <li key={m.metric} className="text-sm flex gap-2">
              <span
                className={
                  m.expected_direction === "increase"
                    ? "text-eco-600"
                    : m.expected_direction === "decrease"
                    ? "text-red-500"
                    : "text-slate-400"
                }
              >
                {DIRECTION_ICON[m.expected_direction]}
              </span>
              <span>
                <span className="font-medium capitalize">{m.metric}</span>
                {" — "}
                {m.explanation}
              </span>
            </li>
          ))}
        </ul>
      </div>

      {rec.implementation_notes.length > 0 && (
        <div>
          <h4 className="text-xs uppercase tracking-wide text-slate-500 font-semibold mb-1">
            Implementation notes
          </h4>
          <ul className="list-disc list-inside text-sm text-slate-700 space-y-0.5">
            {rec.implementation_notes.map((n, i) => (
              <li key={i}>{n}</li>
            ))}
          </ul>
        </div>
      )}

      <div>
        <h4 className="text-xs uppercase tracking-wide text-slate-500 font-semibold mb-1">
          Sources / evidence
        </h4>
        <EvidenceList evidence={rec.evidence} />
      </div>

      <div>
        <h4 className="text-xs uppercase tracking-wide text-slate-500 font-semibold mb-1">
          Assumptions &amp; limitations
        </h4>
        <ul className="list-disc list-inside text-xs text-slate-500 space-y-0.5">
          {rec.limitations.map((l, i) => (
            <li key={i}>{l}</li>
          ))}
        </ul>
      </div>
    </article>
  );
}
