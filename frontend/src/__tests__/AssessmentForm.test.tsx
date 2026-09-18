import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import AssessmentForm from "../components/AssessmentForm";
import type { AssessmentInput } from "../types";

const BASE: AssessmentInput = { human_impact: [] };

describe("AssessmentForm", () => {
  it("renders the required environmental fields", () => {
    render(<AssessmentForm value={BASE} onChange={() => {}} />);
    expect(screen.getByLabelText(/location name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/ecosystem type/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/soil organic carbon/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/soil ph/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/soil moisture/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/rainfall pattern/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/temperature trend/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/land use/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/habitat fragmentation/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/human impact/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/biodiversity.*observations/i)).toBeInTheDocument();
  });

  it("calls onChange with updated location name", () => {
    const onChange = vi.fn();
    render(<AssessmentForm value={BASE} onChange={onChange} />);
    fireEvent.change(screen.getByLabelText(/location name/i), {
      target: { value: "Test Site" },
    });
    expect(onChange).toHaveBeenCalledWith(expect.objectContaining({ location_name: "Test Site" }));
  });

  it("parses comma-separated human impact into an array", () => {
    const onChange = vi.fn();
    render(<AssessmentForm value={BASE} onChange={onChange} />);
    fireEvent.change(screen.getByLabelText(/human impact/i), {
      target: { value: "pesticide use, pollution" },
    });
    expect(onChange).toHaveBeenCalledWith(
      expect.objectContaining({ human_impact: ["pesticide use", "pollution"] })
    );
  });

  it("coerces numeric soil organic carbon input to a number", () => {
    const onChange = vi.fn();
    render(<AssessmentForm value={BASE} onChange={onChange} />);
    fireEvent.change(screen.getByLabelText(/soil organic carbon/i), {
      target: { value: "0.4" },
    });
    expect(onChange).toHaveBeenCalledWith(
      expect.objectContaining({ soil_organic_carbon_percent: 0.4 })
    );
  });
});
