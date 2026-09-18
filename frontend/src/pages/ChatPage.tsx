import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/client";
import EvidenceList from "../components/EvidenceList";
import { useAssessment } from "../context/AssessmentContext";
import type { ChatMessage } from "../types";

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: "assistant",
      content:
        "Hello — I'm the EcoRestore AI scientist. Tell me about your site (in your own words, or " +
        "switch to the Assessment tab for structured input) and I'll identify biodiversity risks " +
        "grounded in retrieved evidence.",
    },
  ]);
  const [input, setInput] = useState("");
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [memorySummary, setMemorySummary] = useState<string>("No ecosystem details captured yet.");
  const [loading, setLoading] = useState(false);
  const { setAssessment } = useAssessment();
  const navigate = useNavigate();

  const send = async () => {
    const text = input.trim();
    if (!text || loading) return;
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setInput("");
    setLoading(true);
    try {
      const res = await api.chat(text, conversationId);
      setConversationId(res.conversation_id);
      setMemorySummary(res.memory_summary);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: res.reply,
          retrieved_evidence: res.retrieved_evidence,
          follow_up_questions: res.follow_up_questions,
        },
      ]);
      if (res.assessment) {
        setAssessment(res.assessment);
      }
    } catch (e) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: `Error: ${e instanceof Error ? e.message : "request failed"}` },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 grid grid-cols-1 md:grid-cols-3 gap-6">
      <div className="md:col-span-2 flex flex-col bg-white rounded-xl border border-slate-200 h-[70vh]">
        <div className="flex-1 overflow-y-auto p-4 space-y-4" data-testid="chat-messages">
          {messages.map((m, i) => (
            <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
              <div
                className={`max-w-[85%] rounded-lg px-3 py-2 text-sm whitespace-pre-wrap ${
                  m.role === "user" ? "bg-eco-600 text-white" : "bg-slate-100 text-slate-800"
                }`}
              >
                {m.content}
                {m.retrieved_evidence && m.retrieved_evidence.length > 0 && (
                  <div className="mt-2 border-t border-slate-200 pt-2">
                    <p className="text-xs font-semibold text-slate-500 mb-1">Retrieved evidence used:</p>
                    <EvidenceList evidence={m.retrieved_evidence} />
                  </div>
                )}
              </div>
            </div>
          ))}
          {loading && <p className="text-sm text-slate-400">Thinking...</p>}
        </div>
        <div className="border-t border-slate-200 p-3 flex gap-2">
          <input
            className="flex-1 rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-eco-500 focus:outline-none focus:ring-1 focus:ring-eco-500"
            placeholder="Describe your site, or answer the follow-up questions..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && send()}
          />
          <button
            type="button"
            onClick={send}
            disabled={loading}
            className="px-4 py-2 rounded-md bg-eco-600 text-white text-sm font-medium hover:bg-eco-700 disabled:opacity-50"
          >
            Send
          </button>
        </div>
      </div>

      <aside className="space-y-4">
        <div className="bg-white rounded-xl border border-slate-200 p-4">
          <h2 className="text-sm font-semibold text-eco-900 mb-2">Conversation memory</h2>
          <p className="text-xs text-slate-600">{memorySummary}</p>
        </div>
        <button
          type="button"
          onClick={() => navigate("/plan")}
          className="w-full px-4 py-2 rounded-md border border-eco-300 text-eco-700 text-sm font-medium hover:bg-eco-50"
        >
          View Recovery Plan
        </button>
      </aside>
    </div>
  );
}
