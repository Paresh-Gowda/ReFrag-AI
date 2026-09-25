import { useLocation } from "react-router-dom";
import { Search, Bell, ShieldCheck, HelpCircle } from "lucide-react";

const routeMeta = {
  "/": {
    badge: "FORENSIC WORKSPACE",
    title: "Operational Dashboard",
  },
  "/scan": {
    badge: "STORAGE ACQUISITION",
    title: "Scan & Detection Engine",
  },
  "/fragments": {
    badge: "INTELLIGENCE GRAPH",
    title: "Fragment Relationship Analysis",
  },
  "/evidence": {
    badge: "ARTIFACT INSPECTOR",
    title: "Digital Evidence Vault",
  },
  "/analytics": {
    badge: "TELEMETRY & METRICS",
    title: "Recovery Analytics",
  },
};

function Topbar() {
  const location = useLocation();
  const meta = routeMeta[location.pathname] || {
    badge: "SECURE ENVIRONMENT",
    title: "ReFrag Forensic System",
  };

  return (
  <header className="topbar">
    <div className="topbar-title">
      <p>{meta.badge} // REFRACTION CORE</p>
      <h2>{meta.title}</h2>
    </div>

    <div className="topbar-actions">
      <div className="search-box">
        <Search size={14} />
        <input
          type="text"
          placeholder="Search artifacts, hashes, fragments..."
        />
      </div>

      <button
        className="icon-button"
        title="System Notifications"
        type="button"
      >
        <Bell size={16} />
      </button>

      <button
        className="icon-button"
        title="Documentation & Help"
        type="button"
      >
        <HelpCircle size={16} />
      </button>

      <div
        className="security-badge"
        title="Memory Isolation & Integrity Active"
      >
        <ShieldCheck size={14} />
        <span>FORENSIC SESSION SECURE</span>
      </div>
    </div>
  </header>
);
}

export default Topbar;