import { useEffect, useState } from "react";
import {
  ShieldCheck,
  AlertTriangle,
  Brain,
  FileSearch,
  Image,
  Target,
  Activity,
  RefreshCw,
  CheckCircle2,
  Layers3,
} from "lucide-react";

import { getEvidence } from "../services/api";
import "../styles/evidence.css";

function percent(value) {
  const n = Number(value);

  if (!Number.isFinite(n)) {
    return 0;
  }

  return n <= 1 ? n * 100 : n;
}

function Evidence() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  async function loadEvidence(showRefresh = false) {
    try {
      if (showRefresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }

      setError("");

      const response = await getEvidence();

      setData(response || {});
    } catch (err) {
      console.error(
        "Failed to load evidence:",
        err
      );

      setError(
        err.message ||
          "Failed to load evidence."
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }

  useEffect(() => {
    loadEvidence();
  }, []);

  if (loading) {
    return (
      <div className="evidence-page">
        <div className="evidence-loading">
          <ShieldCheck size={28} />
          <strong>
            Loading evidence intelligence...
          </strong>
          <span>
            Reading the latest recovery session.
          </span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="evidence-page">
        <div className="evidence-error">
          <AlertTriangle size={22} />

          <div>
            <strong>
              Evidence service unavailable
            </strong>

            <p>{error}</p>

            <button
              onClick={() =>
                loadEvidence(true)
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

  const evidence =
    Array.isArray(data?.evidence)
      ? data.evidence[0]
      : null;

  const activeFile =
    data?.file ||
    evidence?.file ||
    "No active evidence";

  const isVisual =
    evidence?.visual_recovery ||
    evidence?.mode === "visual";

  const similarity = percent(
    evidence?.similarity ??
      evidence?.reconstruction_confidence ??
      0
  );

  const recovered = percent(
    evidence?.recovered_percentage ??
      evidence?.recovered ??
      0
  );

  const damaged = percent(
    evidence?.damaged_percentage ??
      evidence?.damaged ??
      0
  );

  const damageRegions =
    Number(
      evidence?.damage_regions ??
        evidence?.regions ??
        0
    );

  const priority =
    evidence?.priority || "LOW";

  const integrity =
    evidence?.integrity || "unknown";

  const priorityScore =
    percent(
      evidence?.priority_score ?? 0
    );

  return (
    <div className="evidence-page">

      {/* ================================================= */}
      {/* HEADER */}
      {/* ================================================= */}

      <section className="evidence-hero">

        <div>

          <div className="evidence-live">
            <span />
            LIVE EVIDENCE SESSION
          </div>

          <p className="eyebrow">
            DIGITAL EVIDENCE
          </p>

          <h1>
            Evidence Intelligence
          </h1>

          <p className="evidence-description">
            ReFrag AI converts recovery results
            into traceable evidence signals,
            integrity assessments and
            prioritization intelligence.
          </p>

          <div className="evidence-file">

            {isVisual ? (
              <Image size={15} />
            ) : (
              <FileSearch size={15} />
            )}

            <span>
              ACTIVE FILE
            </span>

            <strong>
              {activeFile}
            </strong>

          </div>

        </div>

        <button
          className="evidence-refresh"
          onClick={() =>
            loadEvidence(true)
          }
          disabled={refreshing}
        >
          <RefreshCw
            size={15}
            className={
              refreshing
                ? "evidence-spin"
                : ""
            }
          />

          Refresh
        </button>

      </section>


      {!evidence ? (

        <div className="no-evidence">

          <ShieldCheck size={34} />

          <h2>
            No active evidence
          </h2>

          <p>
            Upload a file from the Scan page
            to generate evidence intelligence.
          </p>

        </div>

      ) : (

        <>

          {/* ================================================= */}
          {/* PRIMARY EVIDENCE */}
          {/* ================================================= */}

          <section className="evidence-primary">

            <div className="evidence-main-card">

              <div className="evidence-card-top">

                <div>

                  <span className="card-label">
                    PRIMARY EVIDENCE
                  </span>

                  <h2>
                    {activeFile}
                  </h2>

                </div>

                <div
                  className={`priority-badge ${priority.toLowerCase()}`}
                >
                  <Target size={14} />
                  {priority}
                </div>

              </div>


              <div className="evidence-score">

                <div className="score-ring">

                  <strong>
                    {similarity.toFixed(1)}
                    <small>%</small>
                  </strong>

                  <span>
                    AI CONFIDENCE
                  </span>

                </div>

                <div className="score-copy">

                  <div>
                    <span>
                      PRIORITY SCORE
                    </span>

                    <strong>
                      {priorityScore.toFixed(1)}
                    </strong>
                  </div>

                  <p>
                    Evidence prioritization combines
                    recovery confidence, integrity
                    signals and reconstruction support.
                  </p>

                </div>

              </div>

            </div>


            {/* INTEGRITY */}

            <div className="integrity-card">

              <div className="card-label">
                INTEGRITY STATUS
              </div>

              <div className="integrity-icon">

                {integrity === "valid" ? (
                  <CheckCircle2 size={27} />
                ) : (
                  <AlertTriangle size={27} />
                )}

              </div>

              <strong>
                {integrity.toUpperCase()}
              </strong>

              <p>
                {evidence.integrity_reason ||
                  "Integrity assessment generated by the recovery engine."}
              </p>

            </div>

          </section>


          {/* ================================================= */}
          {/* VISUAL RECOVERY */}
          {/* ================================================= */}

          {isVisual && (

            <section className="visual-evidence">

              <div className="section-heading">

                <div>

                  <p className="eyebrow">
                    VISUAL RECOVERY
                  </p>

                  <h2>
                    Reference-Assisted Evidence
                  </h2>

                  <p>
                    The uploaded image was compared
                    against the reference database
                    and analyzed for damaged regions.
                  </p>

                </div>

                <div className="visual-match">

                  <Brain size={16} />

                  {similarity.toFixed(2)}%
                  MATCH

                </div>

              </div>


              <div className="visual-metrics">

                <div>
                  <span>
                    REFERENCE
                  </span>

                  <strong>
                    {evidence.reference ||
                      "Matched reference"}
                  </strong>
                </div>

                <div>
                  <span>
                    RECOVERED
                  </span>

                  <strong>
                    {recovered.toFixed(2)}%
                  </strong>
                </div>

                <div>
                  <span>
                    DAMAGED
                  </span>

                  <strong>
                    {damaged.toFixed(2)}%
                  </strong>
                </div>

                <div>
                  <span>
                    DAMAGE REGIONS
                  </span>

                  <strong>
                    {damageRegions}
                  </strong>
                </div>

              </div>


              <div className="evidence-visual-grid">

                <VisualPanel
                  title="REFERENCE"
                  src="/api/image-recovery/output/reference.jpg"
                />

                <VisualPanel
                  title="DAMAGE MAP"
                  src="/api/image-recovery/output/damage_mask.png"
                />

                <VisualPanel
                  title="EVIDENCE MAP"
                  src="/api/image-recovery/output/evidence_map.png"
                />

                <VisualPanel
                  title="RESTORED"
                  src="/api/image-recovery/output/restored_image.png"
                />

              </div>

            </section>

          )}


          {/* ================================================= */}
          {/* EVIDENCE BREAKDOWN */}
          {/* ================================================= */}

          <section className="evidence-breakdown">

            <div className="section-heading">

              <div>

                <p className="eyebrow">
                  EVIDENCE BREAKDOWN
                </p>

                <h2>
                  Recovery Signals
                </h2>

              </div>

            </div>


            <div className="breakdown-grid">

              <EvidenceSignal
                icon={<ShieldCheck size={19} />}
                title="Integrity"
                value={
                  integrity.toUpperCase()
                }
                description={
                  evidence.integrity_reason ||
                  "Current integrity classification."
                }
              />

              <EvidenceSignal
                icon={<Brain size={19} />}
                title="AI Confidence"
                value={`${similarity.toFixed(1)}%`}
                description={
                  isVisual
                    ? "Reference similarity signal."
                    : "Reconstruction confidence signal."
                }
              />

              <EvidenceSignal
                icon={<Layers3 size={19} />}
                title="Evidence Type"
                value={
                  isVisual
                    ? "VISUAL"
                    : "BYTE RECOVERY"
                }
                description={
                  isVisual
                    ? "Reference-assisted visual recovery."
                    : "Fragment-based digital recovery."
                }
              />

              <EvidenceSignal
                icon={<Activity size={19} />}
                title="Priority"
                value={priority}
                description="AI prioritization for analyst review."
              />

            </div>

          </section>


          {/* ================================================= */}
          {/* FORENSIC INTERPRETATION */}
          {/* ================================================= */}

          <section className="interpretation-card">

            <div className="interpretation-icon">
              <ShieldCheck size={21} />
            </div>

            <div>

              <p className="eyebrow">
                EVIDENCE INTERPRETATION
              </p>

              <h3>
                What ReFrag AI found
              </h3>

              <p>
                {isVisual
                  ? `The uploaded image was matched against the reference database with ${similarity.toFixed(
                      2
                    )}% similarity. ${damageRegions} damaged region${
                      damageRegions === 1
                        ? ""
                        : "s"
                    } were identified. Preserved pixels represent direct input evidence, while restored pixels are reference-assisted.`
                  : `The uploaded file produced ${evidence.fragment_count || 0} fragments. The recovery engine analyzed ${
                      evidence.relationships_analyzed || 0
                    } fragment relationships and assigned ${
                      evidence.reconstruction_confidence || 0
                    }% reconstruction confidence.`}
              </p>

            </div>

          </section>

        </>

      )}

    </div>
  );
}


/* ============================================================
   VISUAL PANEL
   ============================================================ */

function VisualPanel({ title, src }) {
  return (
    <div className="visual-panel">

      <div className="visual-panel-header">

        <span>
          {title}
        </span>

        <Activity size={13} />

      </div>

      <div className="visual-image">

        <img
          src={src}
          alt={title}
          onError={(event) => {
            event.currentTarget.style.display =
              "none";
          }}
        />

      </div>

    </div>
  );
}


/* ============================================================
   SIGNAL
   ============================================================ */

function EvidenceSignal({
  icon,
  title,
  value,
  description,
}) {
  return (
    <div className="evidence-signal">

      <div className="signal-icon">
        {icon}
      </div>

      <div>

        <span>
          {title}
        </span>

        <strong>
          {value}
        </strong>

        <p>
          {description}
        </p>

      </div>

    </div>
  );
}

export default Evidence;