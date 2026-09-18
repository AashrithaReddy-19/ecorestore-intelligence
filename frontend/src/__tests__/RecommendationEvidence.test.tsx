import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import RecommendationCard from "../components/RecommendationCard";
import type { Recommendation } from "../types";

const BASE_REC: Recommendation = {
  priority: 1,
  action: "Native mangrove buffer restoration",
  scientific_reasoning: "Mangrove root systems trap sediment and rebuild nursery habitat.",
  impacted_metrics: [
    {
      metric: "habitat connectivity",
      expected_direction: "increase",
      explanation: "Reconnects fragmented tidal habitat.",
    },
  ],
  time_horizon: "long",
  implementation_notes: ["Match species to tidal zone."],
  evidence: [
    {
      source_id: "IUCN_MANGROVE_001",
      title: "Mangroves and coastal ecosystems — issues brief",
      organization: "IUCN",
      year: 2021,
      url: "https://www.iucn.org/resources/issues-brief/mangroves-and-coastal-ecosystems",
      retrieval_score: 0.82,
    },
  ],
  limitations: ["Not a substitute for an on-site ecological survey."],
};

describe("RecommendationCard evidence rendering", () => {
  it("renders action, reasoning, time horizon, and metrics", () => {
    render(<RecommendationCard rec={BASE_REC} />);
    expect(screen.getByText("Native mangrove buffer restoration")).toBeInTheDocument();
    expect(screen.getByText(/mangrove root systems trap sediment/i)).toBeInTheDocument();
    expect(screen.getByText("Long-term")).toBeInTheDocument();
    expect(screen.getByText(/habitat connectivity/i)).toBeInTheDocument();
  });

  it("renders retrieved evidence with clickable source links and scores", () => {
    render(<RecommendationCard rec={BASE_REC} />);
    const link = screen.getByRole("link", { name: /mangroves and coastal ecosystems/i });
    expect(link).toHaveAttribute("href", BASE_REC.evidence[0].url);
    expect(screen.getByText(/IUCN/)).toBeInTheDocument();
    expect(screen.getByText(/score 0\.82/)).toBeInTheDocument();
  });

  it("shows an explicit no-evidence notice when evidence is empty", () => {
    render(<RecommendationCard rec={{ ...BASE_REC, evidence: [] }} />);
    expect(screen.getByText(/no directly matching evidence was retrieved/i)).toBeInTheDocument();
    expect(screen.queryByTestId("evidence-item")).not.toBeInTheDocument();
  });

  it("renders limitations so uncertainty is never hidden", () => {
    render(<RecommendationCard rec={BASE_REC} />);
    expect(screen.getByText(/not a substitute for an on-site ecological survey/i)).toBeInTheDocument();
  });
});
