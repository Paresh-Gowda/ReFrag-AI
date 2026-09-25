import { useEffect, useState } from "react";
import {
  Database,
  ShieldCheck,
  AlertTriangle,
  FileSearch,
  Activity,
  Brain,
  Network,
  Layers3,
  ArrowUpRight,
  CheckCircle2,
  Zap,
} from "lucide-react";

import { getDashboard, getAnalytics } from "../services/api";

import "../styles/dashboard.css";


function Dashboard() {
  const [stats, setStats] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");


  useEffect(() => {
    async function loadDashboard() {
      try {
        setLoading(true);
        setError("");

        const [dashboardData, analyticsData] = await Promise.all([
          getDashboard(),
          getAnalytics(),
        ]);

        setStats(dashboardData?.statistics || {});
        setAnalytics(analyticsData || {});
      } catch (err) {
        console.error("Dashboard error:", err);

        setError(
          err.message ||
          "Unable to connect to ReFrag AI backend."
        );
      } finally {
        setLoading(false);
      }
    }

    loadDashboard();
  }, []);


  /*
   * IMPORTANT:
   * No hooks are used below this point.
   * This keeps the hook order identical on every render.
   */

  if (loading) {
    return (
      <div className="dashboard-page">
        <div className="dashboard-loading">
          <Activity size={20} />
          Loading ReFrag AI intelligence...
        </div>
      </div>
    );
  }


  if (error) {
    return (
      <div className="dashboard-page">
        <div className="dashboard-error">
          <AlertTriangle size={22} />

          <div>
            <strong>
              Backend connection failed
            </strong>

            <span>
              {error}
            </span>
          </div>
        </div>
      </div>
    );
  }


  /*
   * SAFETY FALLBACKS
   */

  const safeStats = stats || {};
  const safeAnalytics = analytics || {};

  const integrity =
    safeAnalytics.integrity || {};

  const priority =
    safeAnalytics.priority || {};


  /*
   * CORE STATISTICS
   */

  const totalFragments =
    Number(
      safeStats.total_fragments || 0
    );

  const candidates =
    Number(
      safeStats.reconstruction_candidates || 0
    );

  const valid =
    Number(
      safeStats.valid_evidence ??
      integrity.valid ??
      0
    );

  const partial =
    Number(
      safeStats.partial_evidence ??
      integrity.partial ??
      0
    );

  const corrupted =
    Number(
      safeStats.corrupted_evidence ??
      integrity.corrupted ??
      0
    );


  /*
   * PRIORITY
   */

  const high =
    Number(
      safeStats.high_priority ??
      priority.HIGH ??
      0
    );

  const medium =
    Number(
      safeStats.medium_priority ??
      priority.MEDIUM ??
      0
    );

  const low =
    Number(
      safeStats.low_priority ??
      priority.LOW ??
      0
    );


  /*
   * CALCULATED METRICS
   */

  const totalIntegrity =
    valid +
    partial +
    corrupted;

  const validPercent =
    totalIntegrity > 0
      ? Math.round(
          (valid / totalIntegrity) * 100
        )
      : 0;

  const recoveryPercent =
    candidates > 0
      ? Math.round(
          (valid / candidates) * 100
        )
      : 0;


  /*
   * STAT CARDS
   */

  const cards = [
    {
      title: "Fragments Scanned",
      value: totalFragments,
      description:
        "Detected storage fragments",
      icon: Database,
    },

    {
      title: "Reconstruction Candidates",
      value: candidates,
      description:
        "Potentially recoverable files",
      icon: FileSearch,
    },

    {
      title: "Valid Evidence",
      value: valid,
      description:
        "Passed integrity validation",
      icon: ShieldCheck,
    },

    {
      title: "Corrupted Evidence",
      value: corrupted,
      description:
        "Requires further analysis",
      icon: AlertTriangle,
    },
  ];


  /*
   * INTEGRITY DATA
   */

  const integrityBars = [
    {
      label: "VALID",
      value: valid,
      className: "valid",
    },

    {
      label: "PARTIAL",
      value: partial,
      className: "partial",
    },

    {
      label: "CORRUPTED",
      value: corrupted,
      className: "corrupted",
    },
  ];


  /*
   * PRIORITY DATA
   */

  const priorityBars = [
    {
      label: "HIGH",
      value: high,
      className: "high",
    },

    {
      label: "MEDIUM",
      value: medium,
      className: "medium",
    },

    {
      label: "LOW",
      value: low,
      className: "low",
    },
  ];


  return (
    <div className="dashboard-page">

      {/* =================================================
          HEADER
      ================================================= */}

      <div className="dashboard-header">

        <div>

          <p className="eyebrow">
            REFRAG AI / COMMAND CENTER
          </p>

          <h1>
            Evidence Recovery Intelligence
          </h1>

          <p>
            AI-assisted reconstruction and digital
            evidence analysis across fragmented data.
          </p>

        </div>


        <div className="system-status">

          <span className="status-dot" />

          <Activity size={15} />

          SYSTEM ONLINE

        </div>

      </div>


      {/* =================================================
          MAIN STATISTICS
      ================================================= */}

      <div className="dashboard-stats">

        {cards.map((card) => {

          const Icon = card.icon;

          return (
            <div
              className="stat-card"
              key={card.title}
            >

              <div className="stat-card-top">

                <div className="stat-icon">
                  <Icon size={20} />
                </div>

                <ArrowUpRight
                  size={16}
                  className="stat-arrow"
                />

              </div>


              <div className="stat-value">
                {card.value.toLocaleString()}
              </div>


              <div className="stat-title">
                {card.title}
              </div>


              <div className="stat-description">
                {card.description}
              </div>

            </div>
          );

        })}

      </div>


      {/* =================================================
          RECOVERY INTELLIGENCE
      ================================================= */}

      <div className="dashboard-section">

        <div className="section-heading">

          <div>

            <p className="eyebrow">
              RECOVERY INTELLIGENCE
            </p>

            <h2>
              Reconstruction Overview
            </h2>

          </div>


          <div className="section-live">

            <Zap size={14} />

            LIVE PIPELINE

          </div>

        </div>


        <div className="recovery-overview">


          {/* RECOVERY HEALTH */}

          <div className="recovery-score-card">

            <div className="overview-icon">
              <ShieldCheck size={21} />
            </div>


            <span>
              RECOVERY HEALTH
            </span>


            <strong>
              {recoveryPercent}%
            </strong>


            <p>
              Valid evidence relative to
              reconstruction candidates.
            </p>


            <div className="large-progress">

              <div
                style={{
                  width: `${Math.min(
                    recoveryPercent,
                    100
                  )}%`,
                }}
              />

            </div>

          </div>


          {/* INTEGRITY */}

          <div className="integrity-card">

            <div className="overview-card-header">

              <div>

                <span>
                  INTEGRITY DISTRIBUTION
                </span>

                <small>
                  {totalIntegrity.toLocaleString()}
                  {" "}candidates analyzed
                </small>

              </div>

              <Layers3 size={20} />

            </div>


            <div className="integrity-bars">

              {integrityBars.map((item) => {

                const percentage =
                  totalIntegrity > 0
                    ? (
                        item.value /
                        totalIntegrity
                      ) * 100
                    : 0;


                return (
                  <div
                    className="integrity-row"
                    key={item.label}
                  >

                    <div className="integrity-label">

                      <span>
                        {item.label}
                      </span>

                      <strong>
                        {item.value}
                      </strong>

                    </div>


                    <div className="integrity-track">

                      <div
                        className={`integrity-fill ${item.className}`}
                        style={{
                          width: `${percentage}%`,
                        }}
                      />

                    </div>


                    <small>
                      {Math.round(
                        percentage
                      )}%
                    </small>

                  </div>
                );

              })}

            </div>

          </div>

        </div>

      </div>


      {/* =================================================
          AI RECOVERY PIPELINE
      ================================================= */}

      <div className="dashboard-section">

        <div className="section-heading">

          <div>

            <p className="eyebrow">
              AI RECOVERY PIPELINE
            </p>

            <h2>
              From fragments to evidence
            </h2>

          </div>

        </div>


        <div className="dashboard-pipeline">

          <PipelineStep
            icon={Database}
            number="01"
            title="Storage Scan"
            value={`${totalFragments.toLocaleString()} fragments`}
          />


          <PipelineConnector />


          <PipelineStep
            icon={Layers3}
            number="02"
            title="Fragment Detection"
            value={`${totalFragments.toLocaleString()} detected`}
          />


          <PipelineConnector />


          <PipelineStep
            icon={Network}
            number="03"
            title="AI Relationships"
            value="ML analysis"
          />


          <PipelineConnector />


          <PipelineStep
            icon={Brain}
            number="04"
            title="Reconstruction"
            value={`${candidates.toLocaleString()} candidates`}
          />


          <PipelineConnector />


          <PipelineStep
            icon={ShieldCheck}
            number="05"
            title="Integrity"
            value={`${valid.toLocaleString()} valid`}
          />

        </div>

      </div>


      {/* =================================================
          EVIDENCE PRIORITY
      ================================================= */}

      <div className="dashboard-section">

        <div className="section-heading">

          <div>

            <p className="eyebrow">
              AI PRIORITIZATION
            </p>

            <h2>
              Evidence Priority
            </h2>

          </div>


          <div className="section-live">

            <Brain size={14} />

            AI CLASSIFICATION

          </div>

        </div>


        <div className="priority-grid">

          {priorityBars.map((item) => {

            const percentage =
              candidates > 0
                ? (
                    item.value /
                    candidates
                  ) * 100
                : 0;


            return (
              <div
                className={`priority-card ${item.className}`}
                key={item.label}
              >

                <div className="priority-card-top">

                  <span>
                    {item.label}
                  </span>

                  <Activity size={17} />

                </div>


                <strong>
                  {item.value.toLocaleString()}
                </strong>


                <small>
                  Evidence candidates
                </small>


                <div className="priority-track">

                  <div
                    className="priority-fill"
                    style={{
                      width: `${Math.min(
                        percentage,
                        100
                      )}%`,
                    }}
                  />

                </div>


                <div className="priority-percent">

                  {Math.round(
                    percentage
                  )}%

                </div>

              </div>
            );

          })}

        </div>

      </div>


      {/* =================================================
          SYSTEM SIGNALS
      ================================================= */}

      <div className="dashboard-section">

        <div className="section-heading">

          <div>

            <p className="eyebrow">
              SYSTEM SIGNALS
            </p>

            <h2>
              Recovery Engine Status
            </h2>

          </div>

        </div>


        <div className="signal-grid">

          <Signal
            icon={Database}
            title="Fragment Scanner"
            status="ACTIVE"
            detail={`${totalFragments.toLocaleString()} fragments available`}
          />


          <Signal
            icon={Network}
            title="Relationship Engine"
            status="ACTIVE"
            detail="Fragment relationships ready"
          />


          <Signal
            icon={Brain}
            title="AI Prioritization"
            status="ACTIVE"
            detail={`${high} high-priority candidates`}
          />


          <Signal
            icon={ShieldCheck}
            title="Integrity Analyzer"
            status="ACTIVE"
            detail={`${validPercent}% valid integrity rate`}
          />

        </div>

      </div>

    </div>
  );
}


/* =========================================================
   PIPELINE STEP
========================================================= */

function PipelineStep({
  icon: Icon,
  number,
  title,
  value,
}) {
  return (
    <div className="dashboard-pipeline-step">

      <span className="pipeline-step-number">
        {number}
      </span>


      <div className="pipeline-step-icon">
        <Icon size={19} />
      </div>


      <strong>
        {title}
      </strong>


      <small>
        {value}
      </small>

    </div>
  );
}


/* =========================================================
   PIPELINE CONNECTOR
========================================================= */

function PipelineConnector() {
  return (
    <div className="dashboard-pipeline-connector">

      <span />
      <span />
      <span />

    </div>
  );
}


/* =========================================================
   SYSTEM SIGNAL
========================================================= */

function Signal({
  icon: Icon,
  title,
  status,
  detail,
}) {
  return (
    <div className="signal-card">

      <div className="signal-icon">
        <Icon size={18} />
      </div>


      <div className="signal-content">

        <div className="signal-title">

          <strong>
            {title}
          </strong>


          <span>

            <CheckCircle2 size={13} />

            {status}

          </span>

        </div>


        <small>
          {detail}
        </small>

      </div>

    </div>
  );
}


export default Dashboard;