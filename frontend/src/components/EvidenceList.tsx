import type { EvidenceRef } from "../types";

export default function EvidenceList({ evidence }: { evidence: EvidenceRef[] }) {
  if (evidence.length === 0) {
    return (
      <p className="text-sm text-amber-700 bg-amber-50 border border-amber-200 rounded-md px-3 py-2">
        No directly matching evidence was retrieved from the knowledge base for this action.
      </p>
    );
  }
  return (
    <ul className="space-y-2" data-testid="evidence-list">
      {evidence.map((e) => (
        <li
          key={e.source_id}
          className="text-sm border border-slate-200 rounded-md px-3 py-2 bg-slate-50"
          data-testid="evidence-item"
        >
          <div className="flex items-center justify-between gap-2">
            <a
              href={e.url}
              target="_blank"
              rel="noreferrer"
              className="font-medium text-eco-700 hover:underline"
            >
              {e.title}
            </a>
            <span className="text-xs text-slate-500 shrink-0">
              score {e.retrieval_score.toFixed(2)}
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            {e.organization} {e.year ? `· ${e.year}` : ""} · {e.source_id}
          </p>
        </li>
      ))}
    </ul>
  );
}
