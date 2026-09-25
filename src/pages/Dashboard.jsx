import { useEffect, useState } from "react";
import {
  Database,
  ShieldCheck,
  AlertTriangle,
  FileSearch,
  Activity,
} from "lucide-react";

import { getDashboard } from "../services/api";

import "../styles/dashboard.css";


function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");


  useEffect(() => {
    async function loadDashboard() {
      try {
        const data = await getDashboard();

        setStats(data.statistics);
      } catch (err) {
        console.error(err);

        setError(
          "Unable to connect to ReFrag AI backend."
        );
      } finally {
        setLoading(false);
      }
    }

    loadDashboard();
  }, []);


  if (loading) {
    return (
      <div className="dashboard-page">
        <div className="dashboard-loading">
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
          <span>{error}</span>
        </div>
      </div>
    );
  }


  const cards = [
    {
      title: "Fragments Scanned",
      value: stats.total_fragments,
      icon: Database,
      description: "Detected storage fragments",
    },
    {
      title: "Reconstruction Candidates",
      value: stats.reconstruction_candidates,
      icon: FileSearch,
      description: "Potentially recoverable files",
    },
    {
      title: "Valid Evidence",
      value: stats.valid_evidence,
      icon: ShieldCheck,
      description: "Passed integrity validation",
    },
    {
      title: "Corrupted Evidence",
      value: stats.corrupted_evidence,
      icon: AlertTriangle,
      description: "Requires further analysis",
    },
  ];


  return (
    <div className="dashboard-page">

      <div className="dashboard-header">

        <div>
          <p className="eyebrow">
            REFRAG AI
          </p>

          <h1>
            Evidence Recovery Dashboard
          </h1>

          <p>
            AI-assisted reconstruction and
            digital evidence analysis.
          </p>
        </div>

        <div className="system-status">
          <Activity size={16} />
          SYSTEM ONLINE
        </div>

      </div>


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

              </div>

              <div className="stat-value">
                {card.value}
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


      <div className="priority-overview">

        <div className="section-heading">

          <div>
            <p className="eyebrow">
              AI PRIORITIZATION
            </p>

            <h2>
              Evidence Priority
            </h2>
          </div>

        </div>


        <div className="priority-grid">

          <div className="priority-card high">
            <span>HIGH</span>
            <strong>
              {stats.high_priority}
            </strong>
            <small>
              Priority evidence
            </small>
          </div>


          <div className="priority-card medium">
            <span>MEDIUM</span>
            <strong>
              {stats.medium_priority}
            </strong>
            <small>
              Requires review
            </small>
          </div>


          <div className="priority-card low">
            <span>LOW</span>
            <strong>
              {stats.low_priority}
            </strong>
            <small>
              Lower confidence
            </small>
          </div>

        </div>

      </div>

    </div>
  );
}


export default Dashboard;