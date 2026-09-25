import {
  Server,
  Cpu,
  ShieldCheck,
  Database,
  Image,
  Trash2,
  Activity,
  CheckCircle2,
} from "lucide-react";
import "../styles/settings.css";

function StatusRow({ icon: Icon, label, value, status = "online" }) {
  return (
    <div className="settings-status-row">
      <div className="settings-status-icon">
        <Icon size={17} />
      </div>

      <div className="settings-status-info">
        <strong>{label}</strong>
        <span>{value}</span>
      </div>

      <div className={`settings-status-pill ${status}`}>
        <span />
        {status === "online" ? "ACTIVE" : "READY"}
      </div>
    </div>
  );
}

function Settings() {
  return (
    <main className="settings-page">

      {/* HEADER */}
      <section className="settings-header">
        <div>
          <p className="eyebrow">SYSTEM // CONTROL</p>
          <h1>System Settings</h1>
          <p>
            Configure and inspect the ReFrag AI forensic recovery environment.
          </p>
        </div>

        <div className="settings-version">
          <span>BUILD</span>
          <strong>HACKATHON // 2026</strong>
        </div>
      </section>

      {/* SYSTEM STATUS */}
      <section className="settings-section">
        <div className="settings-section-heading">
          <div>
            <p className="eyebrow">RUNTIME</p>
            <h2>System Status</h2>
          </div>

          <div className="live-indicator">
            <span />
            SYSTEM ONLINE
          </div>
        </div>

        <div className="settings-card">
          <StatusRow
            icon={Server}
            label="FastAPI Backend"
            value="http://localhost:8000"
          />

          <StatusRow
            icon={Activity}
            label="Recovery Engine"
            value="Local forensic processing"
          />

          <StatusRow
            icon={ShieldCheck}
            label="Forensic Session"
            value="Isolated session state"
          />

          <StatusRow
            icon={Database}
            label="Reference Database"
            value="100 image references"
          />
        </div>
      </section>

      {/* AI PIPELINE */}
      <section className="settings-section">
        <div className="settings-section-heading">
          <div>
            <p className="eyebrow">INTELLIGENCE // PIPELINE</p>
            <h2>AI Recovery Modules</h2>
          </div>
        </div>

        <div className="settings-module-grid">

          <div className="settings-module">
            <Cpu size={18} />
            <div>
              <strong>Fragment Classifier</strong>
              <span>Random Forest</span>
            </div>
            <CheckCircle2 className="module-check" size={17} />
          </div>

          <div className="settings-module">
            <Activity size={18} />
            <div>
              <strong>Relationship Engine</strong>
              <span>Fragment relationship analysis</span>
            </div>
            <CheckCircle2 className="module-check" size={17} />
          </div>

          <div className="settings-module">
            <Database size={18} />
            <div>
              <strong>Reconstruction Engine</strong>
              <span>Evidence chain reconstruction</span>
            </div>
            <CheckCircle2 className="module-check" size={17} />
          </div>

          <div className="settings-module">
            <ShieldCheck size={18} />
            <div>
              <strong>Integrity Analyzer</strong>
              <span>Evidence validation</span>
            </div>
            <CheckCircle2 className="module-check" size={17} />
          </div>

          <div className="settings-module">
            <Activity size={18} />
            <div>
              <strong>Evidence Prioritizer</strong>
              <span>Confidence-based ranking</span>
            </div>
            <CheckCircle2 className="module-check" size={17} />
          </div>

          <div className="settings-module">
            <Image size={18} />
            <div>
              <strong>Visual Recovery</strong>
              <span>Reference-assisted image recovery</span>
            </div>
            <CheckCircle2 className="module-check" size={17} />
          </div>

        </div>
      </section>

      {/* RECOVERY CONFIG */}
      <section className="settings-section">
        <div className="settings-section-heading">
          <div>
            <p className="eyebrow">RECOVERY // PARAMETERS</p>
            <h2>Processing Configuration</h2>
          </div>
        </div>

        <div className="settings-config-grid">

          <div className="config-card">
            <span>BYTE FRAGMENT SIZE</span>
            <strong>4096 bytes</strong>
            <small>Used during digital fragment generation.</small>
          </div>

          <div className="config-card">
            <span>RELATIONSHIP THRESHOLD</span>
            <strong>0.80</strong>
            <small>Minimum confidence for reconstruction links.</small>
          </div>

          <div className="config-card">
            <span>REFERENCE MATCHING</span>
            <strong>Cosine Similarity</strong>
            <small>Visual reference retrieval method.</small>
          </div>

          <div className="config-card">
            <span>EVIDENCE MODEL</span>
            <strong>3-State</strong>
            <small>Recovered / Restored / Unknown.</small>
          </div>

        </div>
      </section>

      {/* DATA */}
      <section className="settings-section">
        <div className="settings-section-heading">
          <div>
            <p className="eyebrow">DATA // MANAGEMENT</p>
            <h2>Session Data</h2>
          </div>
        </div>

        <div className="settings-danger-card">
          <div className="danger-icon">
            <Trash2 size={19} />
          </div>

          <div>
            <strong>Clear Active Recovery Session</strong>
            <p>
              Removes the currently loaded scan and visual recovery session
              from the local runtime.
            </p>
          </div>

          <button type="button" disabled>
            CLEAR SESSION
          </button>
        </div>
      </section>

      {/* FOOTER */}
      <section className="settings-footer">
        <span>ReFrag AI</span>
        <span>•</span>
        <span>AI-Assisted Digital Evidence Recovery</span>
        <span>•</span>
        <span>Local Processing Environment</span>
      </section>

    </main>
  );
}

export default Settings;