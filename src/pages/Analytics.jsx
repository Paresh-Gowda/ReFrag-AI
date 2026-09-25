import { useEffect, useState } from "react";
import {
  BarChart3,
  ShieldCheck,
  AlertTriangle,
  Layers3,
  Activity,
} from "lucide-react";

import { getAnalytics } from "../services/api";
import "../styles/analytics.css";


function Analytics() {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);


  useEffect(() => {
    async function loadAnalytics() {
      try {
        const data = await getAnalytics();
        setAnalytics(data);
      } catch (error) {
        console.error(
          "Failed to load analytics:",
          error
        );
      } finally {
        setLoading(false);
      }
    }

    loadAnalytics();
  }, []);


  if (loading) {
    return (
      <div className="analytics-page">
        <div className="analytics-loading">
          Loading forensic analytics...
        </div>
      </div>
    );
  }


  const integrity =
    analytics?.integrity || {};

  const priority =
    analytics?.priority || {};


  const valid =
    integrity.valid || 0;

  const partial =
    integrity.partial || 0;

  const corrupted =
    integrity.corrupted || 0;

  const high =
    priority.HIGH || 0;

  const medium =
    priority.MEDIUM || 0;

  const low =
    priority.LOW || 0;

  const totalIntegrity =
    valid +
    partial +
    corrupted;


  return (
    <div className="analytics-page">

      {/* HEADER */}

      <div className="analytics-header">

        <div>
          <p className="eyebrow">
            FORENSIC ANALYTICS
          </p>

          <h1>
            Recovery Analytics
          </h1>

          <p>
            Statistical overview of reconstruction,
            integrity and evidence prioritization.
          </p>
        </div>


        <div className="analytics-status">
          <Activity size={17} />
          LIVE PIPELINE DATA
        </div>

      </div>


      {/* OVERVIEW */}

      <div className="analytics-grid">

        <div className="analytics-card">

          <div className="analytics-card-icon">
            <Layers3 size={20} />
          </div>

          <span>
            Reconstruction Candidates
          </span>

          <strong>
            {totalIntegrity}
          </strong>

          <small>
            Files analyzed
          </small>

        </div>


        <div className="analytics-card">

          <div className="analytics-card-icon">
            <ShieldCheck size={20} />
          </div>

          <span>
            Valid Evidence
          </span>

          <strong>
            {valid}
          </strong>

          <small>
            Passed integrity checks
          </small>

        </div>


        <div className="analytics-card">

          <div className="analytics-card-icon">
            <AlertTriangle size={20} />
          </div>

          <span>
            Corrupted
          </span>

          <strong>
            {corrupted}
          </strong>

          <small>
            Require further analysis
          </small>

        </div>


        <div className="analytics-card">

          <div className="analytics-card-icon">
            <BarChart3 size={20} />
          </div>

          <span>
            High Priority
          </span>

          <strong>
            {high}
          </strong>

          <small>
            Evidence candidates
          </small>

        </div>

      </div>


      {/* INTEGRITY */}

      <div className="analytics-section">

        <div className="analytics-section-title">

          <div>
            <p className="eyebrow">
              INTEGRITY ANALYSIS
            </p>

            <h2>
              Reconstruction Health
            </h2>
          </div>

        </div>


        <div className="chart-card">

          <div className="bar-chart">

            <div className="bar-item">

              <div className="bar-value">
                {valid}
              </div>

              <div className="bar-track">

                <div
                  className="bar valid"
                  style={{
                    height: `${
                      totalIntegrity
                        ? (valid / totalIntegrity) * 100
                        : 0
                    }%`,
                  }}
                />

              </div>

              <span>
                VALID
              </span>

            </div>


            <div className="bar-item">

              <div className="bar-value">
                {partial}
              </div>

              <div className="bar-track">

                <div
                  className="bar partial"
                  style={{
                    height: `${
                      totalIntegrity
                        ? (partial / totalIntegrity) * 100
                        : 0
                    }%`,
                  }}
                />

              </div>

              <span>
                PARTIAL
              </span>

            </div>


            <div className="bar-item">

              <div className="bar-value">
                {corrupted}
              </div>

              <div className="bar-track">

                <div
                  className="bar corrupted"
                  style={{
                    height: `${
                      totalIntegrity
                        ? (corrupted / totalIntegrity) * 100
                        : 0
                    }%`,
                  }}
                />

              </div>

              <span>
                CORRUPTED
              </span>

            </div>

          </div>


          <div className="integrity-summary">

            <div>
              <span>Valid</span>
              <strong>{valid}</strong>
            </div>

            <div>
              <span>Partial</span>
              <strong>{partial}</strong>
            </div>

            <div>
              <span>Corrupted</span>
              <strong>{corrupted}</strong>
            </div>

          </div>

        </div>

      </div>


      {/* PRIORITY */}

      <div className="analytics-section">

        <div className="analytics-section-title">

          <div>
            <p className="eyebrow">
              AI PRIORITIZATION
            </p>

            <h2>
              Evidence Distribution
            </h2>
          </div>

        </div>


        <div className="priority-analytics">

          <div className="priority-row">

            <div className="priority-label">
              <span>HIGH</span>
              <strong>{high}</strong>
            </div>

            <div className="priority-track">
              <div
                className="priority-fill high"
                style={{
                  width: `${
                    totalIntegrity
                      ? (high / totalIntegrity) * 100
                      : 0
                  }%`,
                }}
              />
            </div>

          </div>


          <div className="priority-row">

            <div className="priority-label">
              <span>MEDIUM</span>
              <strong>{medium}</strong>
            </div>

            <div className="priority-track">
              <div
                className="priority-fill medium"
                style={{
                  width: `${
                    totalIntegrity
                      ? (medium / totalIntegrity) * 100
                      : 0
                  }%`,
                }}
              />
            </div>

          </div>


          <div className="priority-row">

            <div className="priority-label">
              <span>LOW</span>
              <strong>{low}</strong>
            </div>

            <div className="priority-track">
              <div
                className="priority-fill low"
                style={{
                  width: `${
                    totalIntegrity
                      ? (low / totalIntegrity) * 100
                      : 0
                  }%`,
                }}
              />
            </div>

          </div>

        </div>

      </div>

    </div>
  );
}


export default Analytics;