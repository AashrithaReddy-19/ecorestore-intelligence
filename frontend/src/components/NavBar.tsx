import { NavLink } from "react-router-dom";

const linkClass = ({ isActive }: { isActive: boolean }) =>
  `px-3 py-2 rounded-md text-sm font-medium transition-colors ${
    isActive ? "bg-eco-600 text-white" : "text-eco-900 hover:bg-eco-100"
  }`;

export default function NavBar() {
  return (
    <header className="border-b border-eco-200 bg-white sticky top-0 z-20">
      <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-2xl" aria-hidden>
            🌱
          </span>
          <div>
            <p className="font-semibold leading-tight text-eco-900">EcoRestore Intelligence</p>
            <p className="text-xs text-slate-500 leading-tight">
              Evidence-grounded AI for biodiversity recovery
            </p>
          </div>
        </div>
        <nav className="flex gap-1">
          <NavLink to="/" end className={linkClass}>
            Assessment
          </NavLink>
          <NavLink to="/chat" className={linkClass}>
            AI Scientist Chat
          </NavLink>
          <NavLink to="/plan" className={linkClass}>
            Recovery Plan
          </NavLink>
          <NavLink to="/mrv" className={linkClass}>
            MRV Tracker
          </NavLink>
        </nav>
      </div>
    </header>
  );
}
