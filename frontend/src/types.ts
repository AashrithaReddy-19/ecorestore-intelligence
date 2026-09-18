export interface AssessmentInput {
  location_name?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  ecosystem_type?: string | null;
  land_use?: string | null;
  soil_organic_carbon_percent?: number | null;
  soil_ph?: number | null;
  soil_moisture_percent?: number | null;
  soil_salinity?: string | null;
  rainfall_pattern?: string | null;
  temperature_trend?: string | null;
  habitat_fragmentation?: string | null;
  human_impact: string[];
  species_observations?: string | null;
}

export interface EvidenceRef {
  source_id: string;
  title: string;
  organization: string;
  year: number | null;
  url: string;
  retrieval_score: number;
}

export interface ImpactedMetric {
  metric: string;
  expected_direction: "increase" | "decrease" | "stabilise";
  explanation: string;
}

export interface Recommendation {
  priority: number;
  action: string;
  scientific_reasoning: string;
  impacted_metrics: ImpactedMetric[];
  time_horizon: "short" | "medium" | "long";
  implementation_notes: string[];
  evidence: EvidenceRef[];
  limitations: string[];
}

export interface AssessmentResponse {
  assessment_id: string;
  assessment_summary: string;
  biodiversity_risk_level: "low" | "medium" | "high" | "critical";
  confidence: number;
  confidence_explanation: string;
  variables_considered: string[];
  reasoning_trace: string[];
  recommendations: Recommendation[];
  follow_up_monitoring_metrics: string[];
  missing_critical_fields: string[];
  clarifying_questions: string[];
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  retrieved_evidence?: EvidenceRef[];
  follow_up_questions?: string[];
  created_at?: string;
}

export interface ChatResponse {
  conversation_id: string;
  reply: string;
  follow_up_questions: string[];
  retrieved_evidence: EvidenceRef[];
  memory_summary: string;
  collected_facts: Record<string, unknown>;
  assessment: AssessmentResponse | null;
}

export interface MRVMetricComparison {
  metric: string;
  baseline_value: number | null;
  latest_value: number | null;
  delta: number | null;
  trend: "improved" | "declined" | "no_change" | "insufficient_data";
}

export interface MRVTracker {
  assessment_id: string;
  baseline: Record<string, unknown>;
  observations: Record<string, unknown>[];
  comparisons: MRVMetricComparison[];
  summary: string;
}
