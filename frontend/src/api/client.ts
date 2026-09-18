import type {
  AssessmentInput,
  AssessmentResponse,
  ChatResponse,
  MRVTracker,
} from "../types";

const API_BASE_URL: string =
  (import.meta as unknown as { env: Record<string, string> }).env?.VITE_API_BASE_URL ||
  "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API error ${res.status}: ${body}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  createAssessment: (payload: AssessmentInput) =>
    request<AssessmentResponse>("/api/assessments", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  getAssessment: (id: string) => request<AssessmentResponse>(`/api/assessments/${id}`),

  chat: (message: string, conversationId?: string | null, structuredData?: AssessmentInput) =>
    request<ChatResponse>("/api/chat", {
      method: "POST",
      body: JSON.stringify({
        message,
        conversation_id: conversationId ?? null,
        structured_data: structuredData ?? null,
      }),
    }),

  getConversation: (id: string) => request(`/api/conversations/${id}`),

  createBaseline: (payload: Record<string, unknown>) =>
    request<{ baseline_id: string; assessment_id: string }>("/api/mrv/baselines", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  addObservation: (payload: Record<string, unknown>) =>
    request<{ observation_id: string; baseline_id: string }>("/api/mrv/observations", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  getMrvTracker: (assessmentId: string) => request<MRVTracker>(`/api/mrv/${assessmentId}`),

  health: () => request("/api/health"),
};

export { API_BASE_URL };
