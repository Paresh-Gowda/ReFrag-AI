import { useEffect, useState } from "react";
import {
  Search,
  ShieldCheck,
  AlertTriangle,
  Clock3,
  FileCheck2,
} from "lucide-react";

import { getEvidence } from "../services/api";

import "../styles/evidence.css";


function Evidence() {
  const [evidence, setEvidence] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("ALL");


  useEffect(() => {
    async function loadEvidence() {
      try {
        const data = await getEvidence();

        setEvidence(data.evidence || []);
      } catch (error) {
        console.error(
          "Failed to load evidence:",
          error
        );
      } finally {
        setLoading(false);
      }
    }

    loadEvidence();
  }, []);


  const filteredEvidence = evidence.filter((item) => {

    const matchesSearch =
      String(item.file || "")
        .toLowerCase()
        .includes(search.toLowerCase());

    const matchesFilter =
      filter === "ALL" ||
      String(item.priority || "")
        .toUpperCase() === filter;

    return (
      matchesSearch &&
      matchesFilter
    );
  });


  function getPriorityClass(priority) {
    return String(priority || "")
      .toLowerCase();
  }


  function getStatusIcon(status) {

    const normalized =
      String(status || "")
        .toLowerCase();

    if (normalized === "valid") {
      return <ShieldCheck size={16} />;
    }

    if (normalized === "partial") {
      return <Clock3 size={16} />;
    }

    return <AlertTriangle size={16} />;
  }


  if (loading) {
    return (
      <div className="evidence-page">
        <div className="evidence-loading">
          Loading recovered evidence...
        </div>
      </div>
    );
  }


  return (
    <div className="evidence-page">

      {/* HEADER */}

      <div className="evidence-header">

        <div>
          <p className="eyebrow">
            DIGITAL FORENSICS
          </p>

          <h1>
            Evidence Recovery
          </h1>

          <p>
            Review, validate and prioritize
            reconstructed digital evidence.
          </p>
        </div>

        <div className="evidence-count">
          <FileCheck2 size={18} />
          {evidence.length} candidates
        </div>

      </div>


      {/* CONTROLS */}

      <div className="evidence-controls">

        <div className="evidence-search">

          <Search size={17} />

          <input
            type="text"
            placeholder="Search reconstructed files..."
            value={search}
            onChange={(event) =>
              setSearch(event.target.value)
            }
          />

        </div>


        <div className="evidence-filters">

          {[
            "ALL",
            "HIGH",
            "MEDIUM",
            "LOW",
          ].map((item) => (

            <button
              key={item}
              className={
                filter === item
                  ? "filter active"
                  : "filter"
              }
              onClick={() =>
                setFilter(item)
              }
            >
              {item}
            </button>

          ))}

        </div>

      </div>


      {/* TABLE */}

      <div className="evidence-table-wrapper">

        <table className="evidence-table">

          <thead>
            <tr>

              <th>RANK</th>

              <th>RECONSTRUCTED FILE</th>

              <th>INTEGRITY</th>

              <th>FRAGMENTS</th>

              <th>CONFIDENCE</th>

              <th>PRIORITY</th>

              <th>SCORE</th>

            </tr>
          </thead>


          <tbody>

            {filteredEvidence.map(
              (item, index) => (

                <tr
                  key={
                    item.file ||
                    index
                  }
                >

                  <td>
                    <span className="rank">
                      {item.priority_rank ||
                        index + 1}
                    </span>
                  </td>


                  <td>

                    <div className="file-cell">

                      <strong>
                        {item.file}
                      </strong>

                      <small>
                        {item.explanation}
                      </small>

                    </div>

                  </td>


                  <td>

                    <span
                      className={`status ${
                        String(
                          item.integrity_status ||
                          ""
                        ).toLowerCase()
                      }`}
                    >

                      {getStatusIcon(
                        item.integrity_status
                      )}

                      {String(
                        item.integrity_status ||
                        "UNKNOWN"
                      ).toUpperCase()}

                    </span>

                  </td>


                  <td>
                    {item.fragment_count}
                  </td>


                  <td>

                    <div className="confidence">

                      <div className="confidence-bar">

                        <div
                          className="confidence-fill"
                          style={{
                            width: `${
                              Number(
                                item.reconstruction_confidence ||
                                0
                              ) * 100
                            }%`,
                          }}
                        />

                      </div>

                      <span>
                        {(
                          Number(
                            item.reconstruction_confidence ||
                            0
                          ) * 100
                        ).toFixed(1)}
                        %
                      </span>

                    </div>

                  </td>


                  <td>

                    <span
                      className={`priority-badge ${getPriorityClass(
                        item.priority
                      )}`}
                    >
                      {item.priority}
                    </span>

                  </td>


                  <td>

                    <strong className="score">
                      {Number(
                        item.priority_score || 0
                      ).toFixed(2)}
                    </strong>

                  </td>

                </tr>

              )
            )}

          </tbody>

        </table>


        {filteredEvidence.length === 0 && (

          <div className="no-evidence">
            No evidence matches your filters.
          </div>

        )}

      </div>

    </div>
  );
}


export default Evidence;