import {
  Database,
  FileSearch,
  CheckCircle2,
  AlertTriangle,
  Activity,
} from "lucide-react";

import StatCard from "../components/StatCard";

function Dashboard() {
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

        <button className="scan-button">
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

        <button className="text-button">
          View all →
        </button>

      </div>


      <div className="evidence-table">

        <div className="table-header">
          <span>Artifact</span>
          <span>Type</span>
          <span>Integrity</span>
          <span>Confidence</span>
          <span>Status</span>
        </div>

        <div className="table-row">
          <span className="artifact-name">
            IMG_2048.jpg
          </span>
          <span>JPEG</span>
          <span>92%</span>
          <span>95%</span>
          <span className="status recovered">
            Reconstructed
          </span>
        </div>

        <div className="table-row">
          <span className="artifact-name">
            financial_report.pdf
          </span>
          <span>PDF</span>
          <span>78%</span>
          <span>88%</span>
          <span className="status partial">
            Partial
          </span>
        </div>

        <div className="table-row">
          <span className="artifact-name">
            archive_07.zip
          </span>
          <span>ZIP</span>
          <span>96%</span>
          <span>97%</span>
          <span className="status recovered">
            Reconstructed
          </span>
        </div>

      </div>

    </section>
  );
}

export default Dashboard;