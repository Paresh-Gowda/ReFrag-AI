import { useNavigate } from "react-router-dom";
import {
  Database,
  FileSearch,
  CheckCircle2,
  AlertTriangle,
  Activity,
} from "lucide-react";

import StatCard from "../components/StatCard";
import RecoveryTable from "../components/RecoveryTable";

function Dashboard() {
  const navigate = useNavigate();

  return (
    <section className="dashboard">

      {/* HERO */}

      <div className="dashboard-hero">

        <div>
          <p className="eyebrow">
            AI-ASSISTED DIGITAL FORENSICS
          </p>

          <h1>
            Recover what remains.
            <br />
            <span>Understand what was lost.</span>
          </h1>

          <p className="hero-description">
            ReFrag AI analyzes fragmented and corrupted
            digital data, reconstructs recoverable artifacts,
            and evaluates their integrity and confidence.
          </p>
        </div>

        <button className="scan-button" onClick={() => navigate("/scan")}>
          <Activity size={18} />
          Start New Scan
        </button>

      </div>


      {/* STATS */}

      <div className="stats-grid">

        <StatCard
          title="Fragments Detected"
          value="12,482"
          description="Raw fragments discovered"
          icon={Database}
        />

        <StatCard
          title="File Candidates"
          value="1,823"
          description="Potential recoverable files"
          icon={FileSearch}
        />

        <StatCard
          title="Successfully Reconstructed"
          value="1,146"
          description="Validated artifacts"
          icon={CheckCircle2}
        />

        <StatCard
          title="Partial / Corrupted"
          value="421"
          description="Requires further analysis"
          icon={AlertTriangle}
        />

      </div>


      {/* ANALYSIS AREA */}

      <div className="section-header">
        <div>
          <p className="eyebrow">RECOVERY ANALYSIS</p>
          <h2>Current scan overview</h2>
        </div>

        <span className="scan-status">
          <span />
          Scan Active
        </span>
      </div>


      <div className="analysis-grid">

        <div className="analysis-card chart-placeholder">

          <div className="card-header">
            <div>
              <h3>Recovery Pipeline</h3>
              <p>Fragment processing status</p>
            </div>
          </div>

          <div className="pipeline">

            <div className="pipeline-step completed">
              <strong>12,482</strong>
              <span>Fragments</span>
            </div>

            <div className="pipeline-line" />

            <div className="pipeline-step completed">
              <strong>1,823</strong>
              <span>File Candidates</span>
            </div>

            <div className="pipeline-line" />

            <div className="pipeline-step active">
              <strong>1,146</strong>
              <span>Reconstructed</span>
            </div>

            <div className="pipeline-line" />

            <div className="pipeline-step">
              <strong>86%</strong>
              <span>Validated</span>
            </div>

          </div>

        </div>


        <div className="analysis-card">

          <div className="card-header">
            <div>
              <h3>Integrity Distribution</h3>
              <p>Recovered artifact condition</p>
            </div>
          </div>

          <div className="integrity-list">

            <div>
              <span>High Integrity</span>
              <strong>68%</strong>
            </div>

            <div>
              <span>Partial Recovery</span>
              <strong>24%</strong>
            </div>

            <div>
              <span>Corrupted</span>
              <strong>8%</strong>
            </div>

          </div>

        </div>

      </div>


      {/* RECENT EVIDENCE */}

      <div className="section-header evidence-heading">

        <div>
          <p className="eyebrow">RECOVERED EVIDENCE</p>
          <h2>Recent artifacts</h2>
        </div>

        <button className="text-button" onClick={() => navigate("/evidence")}>
          View all →
        </button>

      </div>

      <RecoveryTable />

    </section>
  );
}

export default Dashboard;