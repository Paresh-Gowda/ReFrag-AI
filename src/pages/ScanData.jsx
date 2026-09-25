import { useState } from "react";

import {
  Upload,
  HardDrive,
  FileSearch,
  Cpu,
  Network,
  ShieldCheck,
  Play,
  CheckCircle2,
  AlertTriangle,
  Activity,
  Link2,
  Target,
  Brain,
  Database,
  RotateCcw,
} from "lucide-react";

import "../styles/scan.css";

function ScanData() {
  const [file, setFile] = useState(null);
  const [scanning, setScanning] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const handleFileChange = (event) => {
    const selectedFile = event.target.files?.[0];

    if (!selectedFile) return;

    setFile(selectedFile);
    setResult(null);
    setError("");
  };

  const startScan = async () => {
    if (!file) {
      setError("Please select a file first.");
      return;
    }

    setScanning(true);
    setResult(null);
    setError("");

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(
        "http://localhost:8000/api/scan",
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      console.log("ReFrag AI RESPONSE:", data);

      if (!response.ok || data?.success === false) {
        throw new Error(
          data?.detail ||
            data?.message ||
            "Scan failed."
        );
      }

      setResult(data);
    } catch (err) {
      console.error("SCAN ERROR:", err);

      setError(
        err.message ||
          "Unable to connect to the backend."
      );
    } finally {
      setScanning(false);
    }
  };

  const resetScan = () => {
    setFile(null);
    setResult(null);
    setError("");
  };

  return (
    <section className="scan-page">

      {/* =====================================================
          HEADER
      ===================================================== */}

      <div className="scan-page-header">

        <div>

          <p className="eyebrow">
            FORENSIC DATA ANALYSIS
          </p>

          <h1>
            Scan damaged storage.
            <br />
            <span>Find what remains.</span>
          </h1>

          <p>
            Upload a controlled storage image or raw
            binary sample. ReFrag AI detects fragments,
            classifies data, analyzes relationships,
            reconstructs candidates, validates integrity,
            and prioritizes evidence.
          </p>

        </div>

      </div>


      {/* =====================================================
          UPLOAD
      ===================================================== */}

      <div className="upload-card">

        <div className="upload-icon">
          <Upload size={25} />
        </div>

        <h2>
          {file
            ? file.name
            : "Select forensic data"}
        </h2>

        <p>
          Upload a disk image, raw binary sample,
          or forensic dataset.
        </p>

        <label className="upload-button">

          <Upload size={17} />

          Choose File

          <input
            type="file"
            hidden
            onChange={handleFileChange}
          />

        </label>

        {file && (

          <div className="selected-file">

            <HardDrive size={17} />

            <div>

              <strong>
                {file.name}
              </strong>

              <span>
                {(file.size / 1024).toFixed(2)} KB
                {" • "}
                Ready for analysis
              </span>

            </div>

            <CheckCircle2 size={17} />

          </div>

        )}

      </div>


      {/* =====================================================
          PIPELINE
      ===================================================== */}

      <div className="scan-section">

        <div className="section-header">

          <div>

            <p className="eyebrow">
              AI RECOVERY PIPELINE
            </p>

            <h2>
              Analysis stages
            </h2>

          </div>

          <button
            className="scan-button"
            disabled={!file || scanning}
            onClick={startScan}
          >

            <Play size={17} />

            {scanning
              ? "Scanning..."
              : "Start Analysis"}

          </button>

        </div>


        <div className="scan-pipeline">

          <PipelineCard
            number="01"
            icon={HardDrive}
            title="Storage Scan"
            description="Read raw storage blocks and identify available data."
            active={scanning}
          />

          <div className="pipeline-arrow">
            →
          </div>

          <PipelineCard
            number="02"
            icon={FileSearch}
            title="Fragment Detection"
            description="Detect file signatures and extract candidate fragments."
          />

          <div className="pipeline-arrow">
            →
          </div>

          <PipelineCard
            number="03"
            icon={Network}
            title="AI Relationship"
            description="Analyze relationships between fragmented data."
          />

          <div className="pipeline-arrow">
            →
          </div>

          <PipelineCard
            number="04"
            icon={Cpu}
            title="Reconstruction"
            description="Build candidate files from related fragments."
          />

          <div className="pipeline-arrow">
            →
          </div>

          <PipelineCard
            number="05"
            icon={ShieldCheck}
            title="Integrity"
            description="Validate structure and recovery confidence."
          />

        </div>

      </div>


      {/* =====================================================
          PROCESSING
      ===================================================== */}

      {scanning && (

        <div className="processing-card">

          <div className="processing-header">

            <div>

              <p className="eyebrow">
                LIVE PROCESSING
              </p>

              <h2>
                ReFrag AI is analyzing the dataset
              </h2>

            </div>

            <div className="processing-indicator">
              <span />
              Processing
            </div>

          </div>


          <div className="processing-bar">
            <div />
          </div>


          <div className="processing-stats">

            <div>
              <strong>SCANNING</strong>
              <span>Storage data</span>
            </div>

            <div>
              <strong>FRAGMENTING</strong>
              <span>Data blocks</span>
            </div>

            <div>
              <strong>ANALYZING</strong>
              <span>ML relationships</span>
            </div>

            <div>
              <strong>RECONSTRUCTING</strong>
              <span>Candidate recovery</span>
            </div>

          </div>

        </div>

      )}


      {/* =====================================================
          ERROR
      ===================================================== */}

      {error && (

        <div className="scan-result error-result">

          <div className="result-title">

            <AlertTriangle size={22} />

            <div>

              <p className="eyebrow">
                ANALYSIS ERROR
              </p>

              <h2>
                Scan failed
              </h2>

            </div>

          </div>

          <p>
            {error}
          </p>

        </div>

      )}


      {/* =====================================================
          RESULT
      ===================================================== */}

      {result && (

        <ScanResult
          result={result}
          onReset={resetScan}
        />

      )}

    </section>
  );
}


/* =========================================================
   PIPELINE CARD
========================================================= */

function PipelineCard({
  number,
  icon: Icon,
  title,
  description,
  active = false,
}) {
  return (

    <div
      className={`pipeline-card ${
        active
          ? "pipeline-active"
          : ""
      }`}
    >

      <div className="pipeline-number">
        {number}
      </div>

      <div className="pipeline-icon">
        <Icon size={21} />
      </div>

      <h3>
        {title}
      </h3>

      <p>
        {description}
      </p>

    </div>
  );
}


/* =========================================================
   RESULT
========================================================= */

function ScanResult({
  result,
  onReset,
}) {

  const analysis =
    result?.analysis || {};

  const file =
    result?.file || {};

  /*
   * Backend currently returns these INSIDE analysis.
   * Fallbacks make the frontend tolerant of older API output.
   */

  const fragments =
    analysis.fragments ||
    result.fragments ||
    [];

  const relationships =
    analysis.relationships ||
    result.relationships ||
    [];


  const confidence = Number(
    analysis.reconstruction_confidence || 0
  );

  const confidencePercent = Math.round(
    confidence * 100
  );


  const priorityScore = Number(
    analysis.priority_score || 0
  );


  const relationshipsAnalyzed =
    Number(
      analysis.relationships_analyzed ??
      relationships.length ??
      0
    );


  const strongRelationships =
    Number(
      analysis.strong_relationships ??
      relationships.filter(
        (item) =>
          Number(
            item.relationship_probability || 0
          ) >= 0.8
      ).length
    );


  const reconstructedCount =
    Number(
      analysis.reconstruction_fragment_count || 0
    );


  return (

    <div className="scan-result">

      {/* ===================================================
          RESULT HEADER
      =================================================== */}

      <div className="result-header">

        <div>

          <p className="eyebrow">
            ANALYSIS COMPLETE
          </p>

          <h2>
            {file.name || "Recovered Dataset"}
          </h2>

          <p>
            ReFrag AI completed the forensic scan
            using fragment classification,
            relationship analysis, reconstruction,
            and integrity validation.
          </p>

        </div>


        <div
          className={`result-status status-${String(
            analysis.integrity || "unknown"
          ).toLowerCase()}`}
        >

          <Activity size={18} />

          {analysis.integrity || "UNKNOWN"}

        </div>

      </div>


      {/* ===================================================
          TOP METRICS
      =================================================== */}

      <div className="result-grid">

        <ResultCard
          label="FILE TYPE"
          value={
            analysis.file_type ||
            file.type ||
            "UNKNOWN"
          }
        />

        <ResultCard
          label="FILE SIZE"
          value={`${(
            Number(file.size || 0) / 1024
          ).toFixed(2)} KB`}
        />

        <ResultCard
          label="FRAGMENTS"
          value={
            analysis.fragment_count ?? 0
          }
        />

        <ResultCard
          label="ENTROPY"
          value={
            analysis.entropy !== undefined
              ? Number(
                  analysis.entropy
                ).toFixed(3)
              : "N/A"
          }
        />

        <ResultCard
          label="RECOVERY"
          value={`${confidencePercent}%`}
        />

        <ResultCard
          label="PRIORITY"
          value={
            analysis.priority || "LOW"
          }
        />

      </div>


      {/* ===================================================
          ML METRICS
      =================================================== */}

      <div className="result-grid ml-grid">

        <ResultCard
          label="RELATIONSHIPS"
          value={relationshipsAnalyzed}
        />

        <ResultCard
          label="STRONG LINKS"
          value={strongRelationships}
        />

        <ResultCard
          label="RECONSTRUCTED"
          value={reconstructedCount}
        />

        <ResultCard
          label="PRIORITY SCORE"
          value={`${priorityScore.toFixed(1)}/100`}
        />

      </div>


      {/* ===================================================
          RECONSTRUCTION CONFIDENCE
      =================================================== */}

      <div className="confidence-section">

        <div className="confidence-header">

          <div>

            <span>
              Reconstruction Confidence
            </span>

            <small>
              Based on ML fragment relationship analysis
            </small>

          </div>

          <strong>
            {confidencePercent}%
          </strong>

        </div>


        <div className="confidence-bar">

          <div
            style={{
              width: `${Math.min(
                confidencePercent,
                100
              )}%`,
            }}
          />

        </div>

      </div>


      {/* ===================================================
          INTEGRITY
      =================================================== */}

      <div className="analysis-panel">

        <div className="analysis-panel-header">

          <div>

            <p className="eyebrow">
              INTEGRITY ANALYSIS
            </p>

            <h2>
              {analysis.integrity ||
                "UNKNOWN"}
            </h2>

          </div>

          <ShieldCheck size={24} />

        </div>


        <p className="integrity-reason">

          {analysis.integrity_reason ||
            "No integrity explanation available."}

        </p>

      </div>


      {/* ===================================================
          FRAGMENT ANALYSIS
      =================================================== */}

      <div className="fragment-section">

        <div className="section-header">

          <div>

            <p className="eyebrow">
              FRAGMENT ANALYSIS
            </p>

            <h2>
              Detected fragments
            </h2>

          </div>

          <span className="fragment-count">
            {fragments.length} fragments
          </span>

        </div>


        {fragments.length === 0 ? (

          <div className="empty-fragments">

            <FileSearch size={24} />

            <p>
              No fragment records returned by the ML engine.
            </p>

          </div>

        ) : (

          <div className="fragment-list">

            {fragments.map(
              (fragment, index) => {

                const classification =
                  Number(
                    fragment.classification_confidence ||
                    0
                  );

                return (

                  <div
                    className="fragment-row"
                    key={
                      fragment.fragment_id ||
                      index
                    }
                  >

                    <div className="fragment-main">

                      <div className="fragment-id">
                        <span>
                          FRAGMENT
                        </span>

                        <strong>
                          {String(
                            fragment.fragment_id ??
                            index + 1
                          ).padStart(
                            2,
                            "0"
                          )}
                        </strong>
                      </div>

                      <span>
                        Offset:{" "}
                        {fragment.offset ?? 0}
                      </span>

                    </div>


                    <div>

                      <span>
                        Size
                      </span>

                      <strong>
                        {fragment.size ?? 0} B
                      </strong>

                    </div>


                    <div>

                      <span>
                        Type
                      </span>

                      <strong>
                        {fragment.predicted_type ||
                          "UNKNOWN"}
                      </strong>

                    </div>


                    <div>

                      <span>
                        Entropy
                      </span>

                      <strong>
                        {fragment.entropy !==
                        undefined
                          ? Number(
                              fragment.entropy
                            ).toFixed(3)
                          : "N/A"}
                      </strong>

                    </div>


                    <div>

                      <span>
                        ML Confidence
                      </span>

                      <strong>
                        {classification > 0
                          ? `${Math.round(
                              classification * 100
                            )}%`
                          : "N/A"}
                      </strong>

                    </div>

                  </div>

                );
              }
            )}

          </div>

        )}

      </div>


      {/* ===================================================
          RELATIONSHIP ANALYSIS
      =================================================== */}

      <div className="fragment-section">

        <div className="section-header">

          <div>

            <p className="eyebrow">
              AI RELATIONSHIP ANALYSIS
            </p>

            <h2>
              Fragment relationships
            </h2>

          </div>

          <span className="fragment-count">
            {relationships.length} links
          </span>

        </div>


        {relationships.length === 0 ? (

          <div className="empty-fragments">

            <Network size={24} />

            <p>
              No relationship records returned.
            </p>

          </div>

        ) : (

          <div className="relationship-list">

            {relationships.map(
              (relationship, index) => {

                const probability =
                  Number(
                    relationship.relationship_probability ??
                    0
                  );

                const probabilityPercent =
                  Math.round(
                    probability * 100
                  );

                const isStrong =
                  probability >= 0.8;


                return (

                  <div
                    className="relationship-row"
                    key={index}
                  >

                    <div className="relationship-pair">

                      <span>
                        F
                        {Number(
                          relationship.fragment_a
                        ) + 1}
                      </span>

                      <Link2 size={16} />

                      <span>
                        F
                        {Number(
                          relationship.fragment_b
                        ) + 1}
                      </span>

                    </div>


                    <div className="relationship-confidence">

                      <div className="relationship-bar">

                        <div
                          style={{
                            width: `${probabilityPercent}%`,
                          }}
                        />

                      </div>

                      <strong>
                        {probabilityPercent}%
                      </strong>

                    </div>


                    <span
                      className={`relationship-badge ${
                        isStrong
                          ? "strong"
                          : "weak"
                      }`}
                    >
                      {isStrong
                        ? "STRONG"
                        : "WEAK"}
                    </span>

                  </div>

                );
              }
            )}

          </div>

        )}

      </div>


      {/* ===================================================
          EVIDENCE PRIORITY
      =================================================== */}

      <div className="analysis-panel">

        <div className="analysis-panel-header">

          <div>

            <p className="eyebrow">
              EVIDENCE PRIORITIZATION
            </p>

            <h2>
              {analysis.priority ||
                "LOW"}
            </h2>

          </div>

          <Target size={24} />

        </div>


        <div className="priority-details">

          <div>

            <span>
              Priority score
            </span>

            <strong>
              {priorityScore.toFixed(1)}
              /100
            </strong>

          </div>


          <div>

            <span>
              Integrity
            </span>

            <strong>
              {analysis.integrity ||
                "UNKNOWN"}
            </strong>

          </div>


          <div>

            <span>
              Reconstruction
            </span>

            <strong>
              {confidencePercent}%
            </strong>

          </div>

        </div>

      </div>


      {/* ===================================================
          RECOVERY ENGINE
      =================================================== */}

      <div className="analysis-panel">

        <div className="analysis-panel-header">

          <div>

            <p className="eyebrow">
              RECOVERY ENGINE
            </p>

            <h2>
              AI-assisted reconstruction
            </h2>

          </div>

          <Brain size={24} />

        </div>


        <div className="pipeline-summary">

          <div>
            <Database size={18} />

            <span>
              {analysis.fragment_count ?? 0}
              {" "}
              fragments detected
            </span>
          </div>


          <div>
            <Network size={18} />

            <span>
              {relationshipsAnalyzed}
              {" "}
              relationships analyzed
            </span>
          </div>


          <div>
            <Cpu size={18} />

            <span>
              {strongRelationships}
              {" "}
              strong relationships
            </span>
          </div>


          <div>
            <ShieldCheck size={18} />

            <span>
              Integrity:
              {" "}
              {analysis.integrity ||
                "UNKNOWN"}
            </span>
          </div>

        </div>

      </div>


      {/* ===================================================
          RESET
      =================================================== */}

      <div className="scan-again">

        <button
          className="reset-scan-button"
          onClick={onReset}
        >
          <RotateCcw size={17} />
          Scan Another File
        </button>

      </div>

    </div>
  );
}


/* =========================================================
   RESULT CARD
========================================================= */

function ResultCard({
  label,
  value,
}) {
  return (

    <div className="result-card">

      <span>
        {label}
      </span>

      <strong>
        {value}
      </strong>

    </div>
  );
}


export default ScanData;