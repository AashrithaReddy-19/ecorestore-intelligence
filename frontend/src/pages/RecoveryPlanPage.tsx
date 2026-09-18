import { Link } from "react-router-dom";
import RecommendationCard from "../components/RecommendationCard";
import { useAssessment } from "../context/AssessmentContext";

const RISK_COLORS: Record<string, string> = {
  low: "bg-eco-100 text-eco-800 border-eco-300",
  medium: "bg-amber-100 text-amber-800 border-amber-300",
  high: "bg-orange-100 text-orange-800 border-orange-300",
  critical: "bg-red-100 text-red-800 border-red-300",
};

export default function RecoveryPlanPage() {
  const { assessment } = useAssessment();

  if (!assessment) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-16 text-center space-y-4">
        <h1 className="text-2xl font-bold text-eco-900">No assessment yet</h1>
        <p className="text-slate-600">
          Submit a structured assessment or chat with the AI scientist first to generate a
          ranked recovery plan.
        </p>
        <div className="flex justify-center gap-3">
          <Link to="/" className="px-4 py-2 rounded-md bg-eco-600 text-white text-sm font-medium">
            Go to Assessment
          </Link>
          <Link to="/chat" className="px-4 py-2 rounded-md border border-eco-300 text-eco-700 text-sm font-medium">
            Go to Chat
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 space-y-8">
      <div className="bg-white rounded-xl border border-slate-200 p-6 space-y-4">
        <div className="flex items-start justify-between gap-4 flex-wrap">
          <h1 className="text-2xl font-bold text-eco-900">Biodiversity Recovery Plan</h1>
          <span
            className={`px-3 py-1 rounded-full text-sm font-semibold border ${RISK_COLORS[assessment.biodiversity_risk_level]}`}
          >
            Risk: {assessment.biodiversity_risk_level.toUpperCase()}
          </span>
        </div>
        <p className="text-slate-700">{assessment.assessment_summary}</p>

        <div className="flex items-center gap-3">
          <div className="flex-1 h-2 rounded-full bg-slate-100 overflow-hidden">
            <div
              className="h-full bg-eco-500"
              style={{ width: `${Math.round(assessment.confidence * 100)}%` }}
            />
          </div>
          <span className="text-sm font-medium text-slate-600">
            {Math.round(assessment.confidence * 100)}% confidence
          </span>
        </div>
        <p className="text-xs text-slate-500">{assessment.confidence_explanation}</p>

        <details className="text-sm">
          <summary className="cursor-pointer font-medium text-eco-700">
            Variables considered ({assessment.variables_considered.length})
          </summary>
          <ul className="list-disc list-inside mt-2 text-slate-600 space-y-0.5">
            {assessment.variables_considered.map((v, i) => (
              <li key={i}>{v}</li>
            ))}
          </ul>
        </details>

        <details className="text-sm">
          <summary className="cursor-pointer font-medium text-eco-700">
            Reasoning trace ({assessment.reasoning_trace.length} steps)
          </summary>
          <ol className="list-decimal list-inside mt-2 text-slate-600 space-y-1">
            {assessment.reasoning_trace.map((step, i) => (
              <li key={i}>{step}</li>
            ))}
          </ol>
        </details>

        {assessment.clarifying_questions.length > 0 && (
          <div className="bg-amber-50 border border-amber-200 rounded-md p-3 text-sm text-amber-800">
            <p className="font-medium mb-1">This plan has limited confidence. Consider providing:</p>
            <ul className="list-disc list-inside">
              {assessment.clarifying_questions.map((q, i) => (
                <li key={i}>{q}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      <div className="space-y-4">
        <h2 className="text-lg font-semibold text-eco-900">
          Ranked interventions ({assessment.recommendations.length})
        </h2>
        {assessment.recommendations.map((rec) => (
          <RecommendationCard key={rec.priority} rec={rec} />
        ))}
      </div>

      {assessment.follow_up_monitoring_metrics.length > 0 && (
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <h2 className="text-sm font-semibold text-eco-900 mb-2">Recommended follow-up monitoring metrics</h2>
          <div className="flex flex-wrap gap-2">
            {assessment.follow_up_monitoring_metrics.map((m) => (
              <span key={m} className="px-2 py-1 rounded-full bg-eco-50 border border-eco-200 text-xs text-eco-700">
                {m}
              </span>
            ))}
          </div>
          <Link to="/mrv" className="inline-block mt-4 text-sm text-eco-700 hover:underline">
            Set up MRV tracking for this assessment →
          </Link>
        </div>
      )}
    </div>
  );
}
