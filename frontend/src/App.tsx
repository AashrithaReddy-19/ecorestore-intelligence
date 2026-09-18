import { Route, Routes } from "react-router-dom";
import NavBar from "./components/NavBar";
import { AssessmentProvider } from "./context/AssessmentContext";
import AssessmentPage from "./pages/AssessmentPage";
import ChatPage from "./pages/ChatPage";
import MRVTrackerPage from "./pages/MRVTrackerPage";
import RecoveryPlanPage from "./pages/RecoveryPlanPage";

export default function App() {
  return (
    <AssessmentProvider>
      <div className="min-h-screen flex flex-col">
        <NavBar />
        <main className="flex-1">
          <Routes>
            <Route path="/" element={<AssessmentPage />} />
            <Route path="/chat" element={<ChatPage />} />
            <Route path="/plan" element={<RecoveryPlanPage />} />
            <Route path="/mrv" element={<MRVTrackerPage />} />
          </Routes>
        </main>
        <footer className="text-center text-xs text-slate-400 py-4">
          EcoRestore Intelligence — built for the Darukaa.Earth AI Biodiversity Intelligence Chatbot Challenge
        </footer>
      </div>
    </AssessmentProvider>
  );
}
