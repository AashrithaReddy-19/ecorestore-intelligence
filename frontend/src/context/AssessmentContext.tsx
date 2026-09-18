import React, { createContext, useContext, useState } from "react";
import type { AssessmentResponse } from "../types";

interface AssessmentContextValue {
  assessment: AssessmentResponse | null;
  setAssessment: (a: AssessmentResponse | null) => void;
}

const AssessmentContext = createContext<AssessmentContextValue | undefined>(undefined);

export function AssessmentProvider({ children }: { children: React.ReactNode }) {
  const [assessment, setAssessment] = useState<AssessmentResponse | null>(null);
  return (
    <AssessmentContext.Provider value={{ assessment, setAssessment }}>
      {children}
    </AssessmentContext.Provider>
  );
}

export function useAssessment() {
  const ctx = useContext(AssessmentContext);
  if (!ctx) throw new Error("useAssessment must be used within AssessmentProvider");
  return ctx;
}
