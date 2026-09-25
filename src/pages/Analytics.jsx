import { useEffect, useState } from "react";
import {
  Activity,
  Brain,
  ShieldCheck,
  Network,
  Image,
  Database,
  Target,
  Zap,
  RefreshCw,
  CheckCircle2,
  AlertTriangle,
  BarChart3,
} from "lucide-react";

import { getAnalytics } from "../services/api";
import "../styles/analytics.css";

function pct(value) {
  const n = Number(value);

  if (!Number.isFinite(n)) {
    return 0;
  }

  return n <= 1 ? n * 100 : n;
}

function Analytics() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  async function loadAnalytics(showRefresh = false) {
    try {
      if (showRefresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }

      setError("");

      const response = await getAnalytics();

      setData(response || {});
    } catch (err) {
      console.error(
        "Failed to load analytics:",
        err
      );

      setError(
        err.message ||
          "Failed to load analytics."
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }

  useEffect(() => {
    loadAnalytics();
  }, []);

  if (loading) {
    return (
      <div className="analytics-page">
        <div className="analytics-loading">
          <BarChart3 size={28} />
          <strong>
            Loading recovery analytics...
          </strong>
          <span>
            Reading the current ReFrag AI session.
          </span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="analytics-page">
        <div className="analytics-error">
          <AlertTriangle size={22} />

          <div>
            <strong>
              Analytics unavailable
            </strong>

            <p>{error}</p>

            <button
              onClick={() =>
                loadAnalytics(true)
              }
            >
              <RefreshCw size={14} />
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  const analytics =
    data?.analytics || {};

  const integrity =
    data?.integrity || {};

  const priority =
    data?.priority || {};

  const modelSignals =
    data?.model_signals || {};

  const activeFile =
    data?.file ||
    "No active scan";

  const isVisual =
    analytics.visual_recovery === true ||
    analytics.mode === "visual";

  const totalFragments =
    Number(
      analytics.total_fragments || 0
    );

  const relationships =
    Number(
      analytics.relationships_analyzed || 0
    );

  const strongRelationships =
    Number(
      analytics.strong_relationships || 0
    );

  const reconstructionConfidence =
    pct(
      analytics.reconstruction_confidence ||
        analytics.similarity ||
        0
    );

  const priorityScore =
    pct(
      analytics.priority_score || 0
    );

  const entropy =
    Number(analytics.entropy || 0);

  const recovered =
    pct(
      analytics.recovered_percentage ||
        0
    );

  const damaged =
    pct(
      analytics.damaged_percentage ||
        0
    );

  const damageRegions =
    Number(
      analytics.damage_regions || 0
    );

  const totalIntegrity =
    Number(integrity.valid || 0) +
    Number(integrity.partial || 0) +
    Number(integrity.corrupted || 0);

  return (
    <div className="analytics-page">

      {/* ================================================= */}
      {/* HEADER */}
      {/* ================================================= */}

      <section className="analytics-hero">

        <div>

          <div className="analytics-live">
            <span />
            LIVE ANALYTICS
          </div>

          <p className="eyebrow">
            RECOVERY ANALYTICS
          </p>

          <h1>
            Intelligence Analytics
          </h1>

          <p className="analytics-description">
            Understand how ReFrag AI interpreted
            the current recovery session, from
            fragment relationships and integrity
            to visual damage and evidence priority.
          </p>

          <div className="analytics-file">

            {isVisual ? (
              <Image size={15} />
            ) : (
              <Database size={15} />
            )}

            <span>
              ACTIVE SESSION
            </span>

            <strong>
              {activeFile}
            </strong>

          </div>

        </div>

        <button
          className="analytics-refresh"
          onClick={() =>
            loadAnalytics(true)
          }
          disabled={refreshing}
        >
          <RefreshCw
            size={15}
            className={
              refreshing
                ? "analytics-spin"
                : ""
            }
          />

          Refresh
        </button>

      </section>


      {/* ================================================= */}
      {/* MODE */}
      {/* ================================================= */}

      <section className="analysis-mode">

        <div className="mode-icon">
          {isVisual ? (
            <Image size={20} />
          ) : (
            <Database size={20} />
          )}
        </div>

        <div>
          <span>
            ANALYSIS MODE
          </span>

          <strong>
            {isVisual
              ? "VISUAL IMAGE RECOVERY"
              : "DIGITAL FRAGMENT RECOVERY"}
          </strong>

          <p>
            {isVisual
              ? "Reference matching, damage analysis and reference-assisted restoration."
              : "Fragment classification, relationship analysis and reconstruction."}
          </p>
        </div>

        <div className="mode-status">
          <CheckCircle2 size={14} />
          ACTIVE
        </div>

      </section>


      {/* ================================================= */}
      {/* TOP METRICS */}
      {/* ================================================= */}

      <section className="analytics-metrics">

        {isVisual ? (
          <>
            <Metric
              icon={<Target size={18} />}
              label="REFERENCE MATCH"
              value={`${reconstructionConfidence.toFixed(
                2
              )}%`}
              detail="Visual similarity"
            />

            <Metric
              icon={<ShieldCheck size={18} />}
              label="RECOVERED"
              value={`${recovered.toFixed(
                2
              )}%`}
              detail="Preserved input evidence"
            />

            <Metric
              icon={<AlertTriangle size={18} />}
              label="DAMAGED"
              value={`${damaged.toFixed(
                2
              )}%`}
              detail="Reference difference"
            />

            <Metric
              icon={<Activity size={18} />}
              label="DAMAGE REGIONS"
              value={damageRegions}
              detail="Detected regions"
            />
          </>
        ) : (
          <>
            <Metric
              icon={<Database size={18} />}
              label="FRAGMENTS"
              value={totalFragments}
              detail="Current file"
            />

            <Metric
              icon={<Network size={18} />}
              label="RELATIONSHIPS"
              value={relationships}
              detail="Analyzed"
            />

            <Metric
              icon={<Brain size={18} />}
              label="STRONG LINKS"
              value={strongRelationships}
              detail="High-confidence links"
            />

            <Metric
              icon={<Target size={18} />}
              label="RECONSTRUCTION"
              value={`${reconstructionConfidence.toFixed(
                1
              )}%`}
              detail="AI confidence"
            />
          </>
        )}

      </section>


      {/* ================================================= */}
      {/* VISUAL ANALYTICS */}
      {/* ================================================= */}

      {isVisual ? (

        <section className="visual-analytics">

          <div className="section-title">

            <div>
              <p className="eyebrow">
                VISUAL FORENSICS
              </p>

              <h2>
                Damage & Recovery Analysis
              </h2>
            </div>

            <div className="section-chip">
              <Image size={14} />
              IMAGE
            </div>

          </div>


          <div className="recovery-comparison">

            <div className="comparison-card">

              <div className="comparison-top">

                <span>
                  PRESERVED
                </span>

                <strong>
                  {recovered.toFixed(2)}%
                </strong>

              </div>

              <div className="comparison-track">
                <span
                  style={{
                    width: `${Math.min(
                      100,
                      Math.max(
                        0,
                        recovered
                      )
                    )}%`,
                  }}
                />
              </div>

              <p>
                Pixels supported directly
                by the uploaded image.
              </p>

            </div>


            <div className="comparison-card damaged">

              <div className="comparison-top">

                <span>
                  DAMAGED / DIFFERENT
                </span>

                <strong>
                  {damaged.toFixed(2)}%
                </strong>

              </div>

              <div className="comparison-track">
                <span
                  style={{
                    width: `${Math.min(
                      100,
                      Math.max(
                        0,
                        damaged
                      )
                    )}%`,
                  }}
                />
              </div>

              <p>
                Pixels differing from the
                matched reference.
              </p>

            </div>

          </div>


          <div className="visual-stat-grid">

            <StatBox
              icon={<Target size={17} />}
              label="REFERENCE SIMILARITY"
              value={`${reconstructionConfidence.toFixed(
                2
              )}%`}
            />

            <StatBox
              icon={<ShieldCheck size={17} />}
              label="PRESERVED EVIDENCE"
              value={`${recovered.toFixed(
                2
              )}%`}
            />

            <StatBox
              icon={<AlertTriangle size={17} />}
              label="DAMAGED AREA"
              value={`${damaged.toFixed(
                2
              )}%`}
            />

            <StatBox
              icon={<Activity size={17} />}
              label="DAMAGE REGIONS"
              value={damageRegions}
            />

          </div>

        </section>

      ) : (

        /* ================================================= */
        /* BYTE ANALYTICS */
        /* ================================================= */

        <section className="byte-analytics">

          <div className="section-title">

            <div>
              <p className="eyebrow">
                FRAGMENT FORENSICS
              </p>

              <h2>
                Recovery Engine Analysis
              </h2>
            </div>

            <div className="section-chip">
              <Database size={14} />
              BYTES
            </div>

          </div>


          <div className="byte-grid">

            <StatBox
              icon={<Database size={17} />}
              label="TOTAL FRAGMENTS"
              value={totalFragments}
            />

            <StatBox
              icon={<Network size={17} />}
              label="RELATIONSHIPS ANALYZED"
              value={relationships}
            />

            <StatBox
              icon={<Zap size={17} />}
              label="STRONG RELATIONSHIPS"
              value={strongRelationships}
            />

            <StatBox
              icon={<Activity size={17} />}
              label="ENTROPY"
              value={
                Number.isFinite(entropy)
                  ? entropy.toFixed(3)
                  : "—"
              }
            />

          </div>

        </section>

      )}


      {/* ================================================= */}
      {/* INTEGRITY */}
      {/* ================================================= */}

      <section className="analytics-section">

        <div className="section-title">

          <div>
            <p className="eyebrow">
              INTEGRITY ANALYSIS
            </p>

            <h2>
              Evidence Integrity
            </h2>

            <p>
              Current integrity classification
              generated by the recovery engine.
            </p>
          </div>

        </div>


        <div className="integrity-layout">

          <div className="integrity-main">

            <IntegrityBar
              label="VALID"
              value={
                Number(
                  integrity.valid || 0
                )
              }
              total={totalIntegrity}
              type="valid"
            />

            <IntegrityBar
              label="PARTIAL"
              value={
                Number(
                  integrity.partial || 0
                )
              }
              total={totalIntegrity}
              type="partial"
            />

            <IntegrityBar
              label="CORRUPTED"
              value={
                Number(
                  integrity.corrupted || 0
                )
              }
              total={totalIntegrity}
              type="corrupted"
            />

          </div>


          <div className="integrity-summary">

            <ShieldCheck size={22} />

            <strong>
              {isVisual
                ? "REFERENCE-ASSISTED"
                : "ENGINE ASSESSED"}
            </strong>

            <span>
              {isVisual
                ? "Visual evidence uses preserved pixels and reference differences."
                : "Integrity is determined from the current reconstruction analysis."}
            </span>

          </div>

        </div>

      </section>


      {/* ================================================= */}
      {/* PRIORITY */}
      {/* ================================================= */}

      <section className="analytics-section">

        <div className="section-title">

          <div>
            <p className="eyebrow">
              EVIDENCE PRIORITIZATION
            </p>

            <h2>
              Analyst Priority
            </h2>

            <p>
              Evidence ranking generated from
              recovery confidence and integrity
              signals.
            </p>
          </div>

          <div className="priority-score">

            <span>
              SCORE
            </span>

            <strong>
              {priorityScore.toFixed(1)}
            </strong>

          </div>

        </div>


        <div className="priority-grid">

          <PriorityCard
            label="HIGH"
            value={priority.HIGH || 0}
          />

          <PriorityCard
            label="MEDIUM"
            value={priority.MEDIUM || 0}
          />

          <PriorityCard
            label="LOW"
            value={priority.LOW || 0}
          />

        </div>

      </section>


      {/* ================================================= */}
      {/* MODEL SIGNALS */}
      {/* ================================================= */}

      <section className="analytics-section">

        <div className="section-title">

          <div>
            <p className="eyebrow">
              AI PIPELINE
            </p>

            <h2>
              Model & Engine Signals
            </h2>

            <p>
              Components contributing to the
              current analysis session.
            </p>
          </div>

        </div>


        <div className="engine-grid">

          <Engine
            icon={<Database size={17} />}
            title="Fragment Classifier"
            active={
              modelSignals.fragment_classifier
            }
            description={
              isVisual
                ? "Not used for visual recovery."
                : "Identifies probable file type."
            }
          />

          <Engine
            icon={<Network size={17} />}
            title="Relationship Engine"
            active={
              modelSignals.relationship_engine
            }
            description={
              isVisual
                ? "Not used for visual recovery."
                : "Analyzes fragment relationships."
            }
          />

          <Engine
            icon={<Brain size={17} />}
            title="Reconstruction Engine"
            active={
              modelSignals.reconstruction_engine
            }
            description={
              isVisual
                ? "Reference-assisted restoration."
                : "Builds candidate evidence chains."
            }
          />

          <Engine
            icon={<ShieldCheck size={17} />}
            title="Integrity Analyzer"
            active={
              modelSignals.integrity_analyzer
            }
            description="Evaluates recovery integrity."
          />

          <Engine
            icon={<Target size={17} />}
            title="Evidence Prioritizer"
            active={
              modelSignals.evidence_prioritizer
            }
            description="Ranks evidence for analyst review."
          />

          <Engine
            icon={<Image size={17} />}
            title="Visual Recovery"
            active={
              modelSignals.visual_recovery ||
              isVisual
            }
            description="Reference database image recovery."
          />

        </div>

      </section>


      {/* ================================================= */}
      {/* FORENSIC NOTE */}
      {/* ================================================= */}

      <section className="analytics-note">

        <ShieldCheck size={19} />

        <div>

          <p className="eyebrow">
            FORENSIC INTERPRETATION
          </p>

          <strong>
            AI output is an analytical signal.
          </strong>

          <p>
            ReFrag AI separates directly preserved
            evidence from reference-assisted or
            model-derived information. Final forensic
            conclusions require analyst validation.
          </p>

        </div>

      </section>

    </div>
  );
}


/* ============================================================
   COMPONENTS
   ============================================================ */

function Metric({
  icon,
  label,
  value,
  detail,
}) {
  return (
    <div className="analytics-metric">

      <div className="metric-icon">
        {icon}
      </div>

      <div>
        <span>{label}</span>

        <strong>{value}</strong>

        <small>{detail}</small>
      </div>

    </div>
  );
}


function StatBox({
  icon,
  label,
  value,
}) {
  return (
    <div className="stat-box">

      <div className="stat-icon">
        {icon}
      </div>

      <span>
        {label}
      </span>

      <strong>
        {value}
      </strong>

    </div>
  );
}


function IntegrityBar({
  label,
  value,
  total,
  type,
}) {
  const percentage =
    total > 0
      ? (value / total) * 100
      : 0;

  return (
    <div className="integrity-bar-row">

      <div className="integrity-bar-label">

        <span className={`integrity-dot ${type}`} />

        <strong>
          {label}
        </strong>

        <span>
          {value}
        </span>

      </div>

      <div className="integrity-track">

        <span
          className={type}
          style={{
            width: `${percentage}%`,
          }}
        />

      </div>

      <small>
        {percentage.toFixed(1)}%
      </small>

    </div>
  );
}


function PriorityCard({
  label,
  value,
}) {
  return (
    <div
      className={`priority-card ${label.toLowerCase()}`}
    >

      <div className="priority-card-top">

        <span>
          {label}
        </span>

        <Target size={15} />

      </div>

      <strong>
        {value}
      </strong>

      <small>
        evidence item
        {Number(value) === 1
          ? ""
          : "s"}
      </small>

    </div>
  );
}


function Engine({
  icon,
  title,
  active,
  description,
}) {
  return (
    <div
      className={`engine-card ${
        active ? "active" : "inactive"
      }`}
    >

      <div className="engine-icon">
        {icon}
      </div>

      <div className="engine-copy">

        <strong>
          {title}
        </strong>

        <span>
          {description}
        </span>

      </div>

      <div className="engine-state">

        <span />

        {active
          ? "ACTIVE"
          : "IDLE"}

      </div>

    </div>
  );
}

export default Analytics;