import {
  useEffect,
  useState,
} from "react";

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
  Image as ImageIcon,
  Search,
  ScanLine,
  Map,
  Sparkles,
} from "lucide-react";

import "../styles/scan.css";
import {
  getDashboard,
  getVisualRecoveryResult,
  scanFile,
  recoverImage,
  clearLiveSession,
} from "../services/api";

const API_BASE = "http://localhost:8000";


/* =========================================================
   MAIN SCAN PAGE
========================================================= */

function ScanData() {
  const [file, setFile] = useState(null);
  const [scanning, setScanning] = useState(false);

  const [result, setResult] = useState(null);
  const [visualResult, setVisualResult] = useState(null);

  const [mode, setMode] = useState(null);
  const [error, setError] = useState("");
  // ============================================================
// RESTORE EXISTING LIVE SESSION
// ============================================================

useEffect(() => {

  let mounted = true;

  const restoreSession = async () => {

    try {

      // ------------------------------------------------------
      // Ask backend whether a live session already exists.
      // ------------------------------------------------------

      const dashboard =
        await getDashboard();

      if (
        !mounted ||
        !dashboard?.active_scan
      ) {
        return;
      }

      const sessionMode =
        dashboard.mode ||
        dashboard.analysis?.mode ||
        "forensic";

      // ------------------------------------------------------
      // VISUAL SESSION
      // ------------------------------------------------------

      if (
        sessionMode === "visual"
      ) {

        const visual =
          await getVisualRecoveryResult();

        if (
          !mounted ||
          !visual?.active
        ) {
          return;
        }

        const restoredVisualResult = {

          success: true,

          message:
            "Existing visual recovery session restored.",

          mode: "visual",

          file: {
            name:
              dashboard.file ||
              visual.result?.input?.filename ||
              "Recovered Image",
          },

          result:
            visual.result,

          outputs:
            visual.outputs,

          reference:
            visual.reference,
        };

        setVisualResult(
          restoredVisualResult
        );

        setResult(null);

        setMode(
          "visual"
        );

        return;
      }

      // ------------------------------------------------------
      // FORENSIC SESSION
      // ------------------------------------------------------

      if (
        sessionMode === "forensic"
      ) {

        const analysis =
          dashboard.analysis ||
          {};

        const restoredForensicResult = {

          success: true,

          message:
            "Existing forensic scan session restored.",

          mode: "forensic",

          file: {
            name:
              dashboard.file ||
              "Recovered Dataset",
          },

          analysis,
        };

        setResult(
          restoredForensicResult
        );

        setVisualResult(null);

        setMode(
          "forensic"
        );
      }

    } catch (err) {

      console.warn(
        "No previous ReFrag session could be restored:",
        err
      );

    }

  };

  restoreSession();

  return () => {
    mounted = false;
  };

}, []);


  /* -------------------------------------------------------
     IMAGE DETECTION
  ------------------------------------------------------- */

  const isImageFile = (selectedFile) => {
    if (!selectedFile) return false;

    const imageTypes = [
      "image/jpeg",
      "image/jpg",
      "image/png",
      "image/webp",
    ];

    return (
      imageTypes.includes(selectedFile.type) ||
      /\.(jpg|jpeg|png|webp)$/i.test(
        selectedFile.name
      )
    );
  };


  /* -------------------------------------------------------
     FILE SELECTION
  ------------------------------------------------------- */

  const handleFileChange = (event) => {
    const selectedFile =
      event.target.files?.[0];

    if (!selectedFile) return;

    const visual = isImageFile(selectedFile);

    setFile(selectedFile);

    setResult(null);
    setVisualResult(null);
    setError("");

    setMode(
      visual
        ? "visual"
        : "forensic"
    );
  };


  /* -------------------------------------------------------
     START ANALYSIS
  ------------------------------------------------------- */

  const startScan = async () => {
    if (!file) {
      setError(
        "Please select a file first."
      );
      return;
    }

    setScanning(true);
    setResult(null);
    setVisualResult(null);
    setError("");

    try {
      const formData =
        new FormData();

      formData.append(
        "file",
        file
      );

      const visual =
        isImageFile(file);

      const endpoint = visual
        ? `${API_BASE}/api/image-recovery`
        : `${API_BASE}/api/scan`;

      console.log(
        `ReFrag AI → ${
          visual
            ? "VISUAL RECOVERY"
            : "FORENSIC SCAN"
        }`
      );

      const response =
        await fetch(
          endpoint,
          {
            method: "POST",
            body: formData,
          }
        );

      let data;

      try {
        data =
          await response.json();
      } catch {
        throw new Error(
          "Backend returned an invalid response."
        );
      }

      console.log(
        "ReFrag AI RESPONSE:",
        data
      );

      if (
        !response.ok ||
        data?.success === false
      ) {
        throw new Error(
          data?.detail ||
            data?.message ||
            "Analysis failed."
        );
      }

      if (visual) {
        setVisualResult(data);
        setMode("visual");
      } else {
        setResult(data);
        setMode("forensic");
      }
    } catch (err) {
      console.error(
        "SCAN ERROR:",
        err
      );

      setError(
        err.message ||
          "Unable to connect to the ReFrag AI backend."
      );
    } finally {
      setScanning(false);
    }
  };


  /* -------------------------------------------------------
     RESET
  ------------------------------------------------------- */

  const resetScan = () => {
    setFile(null);
    setResult(null);
    setVisualResult(null);
    setError("");
    setMode(null);
  };


  return (
    <section className="scan-page">

      {/* ===================================================
          HEADER
      =================================================== */}

      <div className="scan-page-header">

        <div>

          <p className="eyebrow">
            FORENSIC DATA ANALYSIS
          </p>

          <h1>
            Recover what remains.
            <br />
            <span>
              Understand what was lost.
            </span>
          </h1>

          <p>
            Upload forensic data or a
            damaged image. ReFrag AI
            analyzes fragmented data,
            reconstructs recoverable
            information, or performs
            visual recovery using its
            reference database.
          </p>

        </div>

      </div>


      {/* ===================================================
          UPLOAD
      =================================================== */}

      <div className="upload-card">

        <div className="upload-icon">
          <Upload size={25} />
        </div>

        <h2>
          {file
            ? file.name
            : "Select forensic data or damaged image"}
        </h2>

        <p>
          Upload a disk image, raw
          binary sample, forensic
          dataset, or damaged image.
        </p>

        <label className="upload-button">

          <Upload size={17} />

          Choose File

          <input
            type="file"
            hidden
            accept="
              .jpg,
              .jpeg,
              .png,
              .webp,
              .bin,
              .img,
              .dd,
              .raw,
              */*
            "
            onChange={
              handleFileChange
            }
          />

        </label>


        {file && (

          <div className="selected-file">

            {mode === "visual" ? (
              <ImageIcon size={17} />
            ) : (
              <HardDrive size={17} />
            )}

            <div>

              <strong>
                {file.name}
              </strong>

              <span>
                {(file.size / 1024).toFixed(2)}
                {" KB • "}

                {mode === "visual"
                  ? "Visual recovery ready"
                  : "Forensic analysis ready"}
              </span>

            </div>

            <CheckCircle2 size={17} />

          </div>

        )}

      </div>


      {/* ===================================================
          DETECTED MODE
      =================================================== */}

      {file && (

        <div className="scan-section">

          <div className="section-header">

            <div>

              <p className="eyebrow">
                ANALYSIS MODE
              </p>

              <h2>
                {mode === "visual"
                  ? "Visual Image Recovery"
                  : "Digital Evidence Recovery"}
              </h2>

            </div>

            <div className="processing-indicator">

              {mode === "visual" ? (
                <>
                  <ImageIcon size={16} />
                  Image detected
                </>
              ) : (
                <>
                  <HardDrive size={16} />
                  Forensic data detected
                </>
              )}

            </div>

          </div>

        </div>

      )}


      {/* ===================================================
          PIPELINE
      =================================================== */}

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
            disabled={
              !file || scanning
            }
            onClick={startScan}
          >

            <Play size={17} />

            {scanning
              ? "Analyzing..."
              : mode === "visual"
                ? "Start Visual Recovery"
                : "Start Analysis"}

          </button>

        </div>


        {mode === "visual" ? (

          <div className="scan-pipeline">

            <PipelineCard
              number="01"
              icon={ImageIcon}
              title="Image Analysis"
              description="Inspect the uploaded damaged image."
              active={scanning}
            />

            <div className="pipeline-arrow">
              →
            </div>

            <PipelineCard
              number="02"
              icon={ScanLine}
              title="Feature Extraction"
              description="Extract color, structure and visual features."
            />

            <div className="pipeline-arrow">
              →
            </div>

            <PipelineCard
              number="03"
              icon={Search}
              title="Reference Search"
              description="Search the 100-image reference database."
            />

            <div className="pipeline-arrow">
              →
            </div>

            <PipelineCard
              number="04"
              icon={Map}
              title="Damage Analysis"
              description="Locate damaged and preserved regions."
            />

            <div className="pipeline-arrow">
              →
            </div>

            <PipelineCard
              number="05"
              icon={Sparkles}
              title="Restoration"
              description="Generate reference-assisted restoration evidence."
            />

          </div>

        ) : (

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

        )}

      </div>


      {/* ===================================================
          PROCESSING
      =================================================== */}

      {scanning && (

        <div className="processing-card">

          <div className="processing-header">

            <div>

              <p className="eyebrow">
                LIVE PROCESSING
              </p>

              <h2>
                ReFrag AI is analyzing the input
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


          {mode === "visual" ? (

            <div className="processing-stats">

              <div>
                <strong>
                  ANALYZING
                </strong>
                <span>
                  Image structure
                </span>
              </div>

              <div>
                <strong>
                  SEARCHING
                </strong>
                <span>
                  Reference database
                </span>
              </div>

              <div>
                <strong>
                  COMPARING
                </strong>
                <span>
                  Visual similarity
                </span>
              </div>

              <div>
                <strong>
                  RESTORING
                </strong>
                <span>
                  Reference evidence
                </span>
              </div>

            </div>

          ) : (

            <div className="processing-stats">

              <div>
                <strong>
                  SCANNING
                </strong>
                <span>
                  Storage data
                </span>
              </div>

              <div>
                <strong>
                  FRAGMENTING
                </strong>
                <span>
                  Data blocks
                </span>
              </div>

              <div>
                <strong>
                  ANALYZING
                </strong>
                <span>
                  ML relationships
                </span>
              </div>

              <div>
                <strong>
                  RECONSTRUCTING
                </strong>
                <span>
                  Candidate recovery
                </span>
              </div>

            </div>

          )}

        </div>

      )}


      {/* ===================================================
          ERROR
      =================================================== */}

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


      {/* ===================================================
          VISUAL RESULT
      =================================================== */}

      {visualResult && (

        <VisualRecoveryResult
          result={visualResult}
          onReset={resetScan}
        />

      )}


      {/* ===================================================
          FORENSIC RESULT
      =================================================== */}

      {result && (

        <ForensicScanResult
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
   VISUAL RECOVERY RESULT
========================================================= */

function VisualRecoveryResult({
  result,
  onReset,
}) {
  const data =
    result?.result || {};

  const input =
    data.input || {};

  const reference =
    data.reference_match || {};

  const damage =
    data.damage_analysis || {};

  const evidence =
    data.evidence || {};

  const outputs =
    data.outputs || {};


  const similarity =
    Number(
      reference.similarity_percent || 0
    );

  const recovered =
    Number(
      damage.recovered_percent || 0
    );

  const damaged =
    Number(
      damage.damaged_percent || 0
    );


  /* -------------------------------------------------------
     OUTPUT IMAGE URLS
  ------------------------------------------------------- */

  const referenceImage =
    outputs.reference_image
      ? `${API_BASE}${outputs.reference_image}`
      : `${API_BASE}/api/image-recovery/output/reference.jpg`;

  const damageMask =
    outputs.damage_mask
      ? `${API_BASE}${outputs.damage_mask}`
      : null;

  const evidenceMap =
    outputs.evidence_map
      ? `${API_BASE}${outputs.evidence_map}`
      : null;

  const restoredImage =
    outputs.restored_image
      ? `${API_BASE}${outputs.restored_image}`
      : null;


  return (

    <div className="scan-result visual-recovery-result">

      {/* =================================================
          HEADER
      ================================================= */}

      <div className="result-header">

        <div>

          <p className="eyebrow">
            VISUAL RECOVERY COMPLETE
          </p>

          <h2>
            {input.filename ||
              "Damaged Image"}
          </h2>

          <p>
            ReFrag AI searched the
            reference database,
            identified the closest
            visual reference,
            analyzed damaged regions,
            and generated
            reference-assisted
            restoration evidence.
          </p>

        </div>

        <div className="result-status status-valid">

          <ImageIcon size={18} />

          IMAGE RECOVERY

        </div>

      </div>


      {/* =================================================
          TOP METRICS
      ================================================= */}

      <div className="result-grid">

        <ResultCard
          label="REFERENCE MATCH"
          value={`${similarity.toFixed(2)}%`}
        />

        <ResultCard
          label="RECOVERED"
          value={`${recovered.toFixed(1)}%`}
        />

        <ResultCard
          label="DAMAGED"
          value={`${damaged.toFixed(1)}%`}
        />

        <ResultCard
          label="DAMAGE REGIONS"
          value={
            damage.damage_regions ??
            0
          }
        />

      </div>


      {/* =================================================
          REFERENCE MATCH
      ================================================= */}

      <div className="analysis-panel">

        <div className="analysis-panel-header">

          <div>

            <p className="eyebrow">
              REFERENCE DATABASE
            </p>

            <h2>
              Best visual match
            </h2>

          </div>

          <Target size={24} />

        </div>


        <div className="visual-reference-card">

          <div className="reference-image-container">

            <img
              src={referenceImage}
              alt="Matched reference"
              onError={(event) => {
                event.currentTarget.style.display =
                  "none";
              }}
            />

            <div className="reference-placeholder">

              <ImageIcon size={30} />

              <span>
                {reference.reference_filename ||
                  "Reference image"}
              </span>

            </div>

          </div>


          <div className="reference-details">

            <span>
              MATCHED REFERENCE
            </span>

            <strong>
              {reference.reference_filename ||
                "Unknown"}
            </strong>


            <div className="reference-score">

              <div className="confidence-bar">

                <div
                  style={{
                    width: `${Math.min(
                      similarity,
                      100
                    )}%`,
                  }}
                />

              </div>

              <strong>
                {similarity.toFixed(2)}%
              </strong>

            </div>


            <p>
              Reference ID:{" "}
              {reference.reference_id ||
                "N/A"}
            </p>

          </div>

        </div>

      </div>


      {/* =================================================
          RECOVERY METRICS
      ================================================= */}

      <div className="confidence-section">

        <div className="confidence-header">

          <div>

            <span>
              Preserved Input Evidence
            </span>

            <small>
              Pixels directly supported
              by the uploaded image
            </small>

          </div>

          <strong>
            {recovered.toFixed(1)}%
          </strong>

        </div>


        <div className="confidence-bar">

          <div
            style={{
              width: `${Math.min(
                recovered,
                100
              )}%`,
            }}
          />

        </div>

      </div>


      {/* =================================================
          DAMAGE ANALYSIS
      ================================================= */}

      <div className="analysis-panel">

        <div className="analysis-panel-header">

          <div>

            <p className="eyebrow">
              DAMAGE ANALYSIS
            </p>

            <h2>
              Damaged regions
            </h2>

          </div>

          <ScanLine size={24} />

        </div>


        <div className="result-grid ml-grid">

          <ResultCard
            label="TOTAL PIXELS"
            value={
              damage.total_pixels
                ?.toLocaleString() ||
              "0"
            }
          />

          <ResultCard
            label="PRESERVED PIXELS"
            value={
              damage.preserved_pixels
                ?.toLocaleString() ||
              "0"
            }
          />

          <ResultCard
            label="DAMAGED PIXELS"
            value={
              damage.damaged_pixels
                ?.toLocaleString() ||
              "0"
            }
          />

          <ResultCard
            label="REGIONS"
            value={
              damage.damage_regions ??
              0
            }
          />

        </div>


        {damage.regions?.length > 0 && (

          <div className="fragment-section">

            <div className="section-header">

              <div>

                <p className="eyebrow">
                  REGION DETAILS
                </p>

                <h2>
                  Detected damage
                </h2>

              </div>

            </div>


            <div className="fragment-list">

              {damage.regions.map(
                (region, index) => (

                  <div
                    className="fragment-row"
                    key={
                      region.region_id ||
                      index
                    }
                  >

                    <div className="fragment-main">

                      <div className="fragment-id">

                        <span>
                          REGION
                        </span>

                        <strong>
                          {String(
                            region.region_id ||
                              index + 1
                          ).padStart(
                            2,
                            "0"
                          )}
                        </strong>

                      </div>

                      <span>
                        Position:{" "}
                        {region.x ?? 0},{" "}
                        {region.y ?? 0}
                      </span>

                    </div>


                    <div>

                      <span>
                        Size
                      </span>

                      <strong>
                        {region.width ??
                          0}
                        {" × "}
                        {region.height ??
                          0}
                      </strong>

                    </div>


                    <div>

                      <span>
                        Area
                      </span>

                      <strong>
                        {region.area ??
                          0}
                        {" px"}
                      </strong>

                    </div>

                  </div>

                )
              )}

            </div>

          </div>

        )}

      </div>


      {/* =================================================
          OUTPUTS
      ================================================= */}

      <div className="analysis-panel">

        <div className="analysis-panel-header">

          <div>

            <p className="eyebrow">
              RECOVERY OUTPUTS
            </p>

            <h2>
              Reconstruction evidence
            </h2>

          </div>

          <Brain size={24} />

        </div>


        <div className="visual-output-grid">

          <OutputImage
            title="Damage Mask"
            description="Detected damaged regions"
            src={damageMask}
          />

          <OutputImage
            title="Evidence Map"
            description="Preserved and damaged evidence"
            src={evidenceMap}
          />

          <OutputImage
            title="Restored Image"
            description="Reference-assisted restoration"
            src={restoredImage}
          />

        </div>

      </div>


      {/* =================================================
          EVIDENCE
      ================================================= */}

      <div className="analysis-panel">

        <div className="analysis-panel-header">

          <div>

            <p className="eyebrow">
              EVIDENCE INTERPRETATION
            </p>

            <h2>
              What ReFrag AI knows
            </h2>

          </div>

          <ShieldCheck size={24} />

        </div>


        <div className="pipeline-summary">

          <div>

            <CheckCircle2 size={18} />

            <span>
              Preserved →{" "}
              {formatEvidence(
                evidence.preserved_content,
                "DIRECT INPUT EVIDENCE"
              )}
            </span>

          </div>


          <div>

            <AlertTriangle size={18} />

            <span>
              Damaged →{" "}
              {formatEvidence(
                evidence.damaged_content,
                "DIFFERENCE FROM REFERENCE"
              )}
            </span>

          </div>


          <div>

            <Sparkles size={18} />

            <span>
              Restored →{" "}
              {formatEvidence(
                evidence.restored_content,
                "REFERENCE ASSISTED"
              )}
            </span>

          </div>

        </div>

      </div>


      {/* =================================================
          FORENSIC INTERPRETATION
      ================================================= */}

      <div className="analysis-panel">

        <div className="analysis-panel-header">

          <div>

            <p className="eyebrow">
              FORENSIC INTERPRETATION
            </p>

            <h2>
              Recovery vs restoration
            </h2>

          </div>

          <ShieldCheck size={24} />

        </div>


        <div className="pipeline-summary">

          <div>

            <CheckCircle2 size={18} />

            <span>
              Recovered = evidence
              directly supported
              by input
            </span>

          </div>


          <div>

            <Sparkles size={18} />

            <span>
              Restored = reference-assisted
              or inferred content
            </span>

          </div>


          <div>

            <AlertTriangle size={18} />

            <span>
              Reference difference
              does not automatically
              prove deletion
            </span>

          </div>

        </div>

      </div>


      {/* =================================================
          RESET
      ================================================= */}

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
   OUTPUT IMAGE
========================================================= */

function OutputImage({
  title,
  description,
  src,
}) {
  return (

    <div className="visual-output-card">

      <div className="visual-output-header">

        <div>

          <strong>
            {title}
          </strong>

          <span>
            {description}
          </span>

        </div>

      </div>


      <div className="visual-output-image">

        {src ? (

          <img
            src={src}
            alt={title}
          />

        ) : (

          <div className="visual-output-placeholder">

            <ImageIcon size={28} />

            <span>
              Output unavailable
            </span>

          </div>

        )}

      </div>

    </div>
  );
}


/* =========================================================
   EVIDENCE FORMATTER
========================================================= */

function formatEvidence(
  value,
  fallback
) {
  if (!value) return fallback;

  return String(value)
    .replaceAll("_", " ")
    .toLowerCase()
    .replace(
      /\b\w/g,
      (letter) =>
        letter.toUpperCase()
    );
}


/* =========================================================
   FORENSIC RESULT
========================================================= */

function ForensicScanResult({
  result,
  onReset,
}) {
  const analysis =
    result?.analysis || {};

  const file =
    result?.file || {};

  const fragments =
    analysis.fragments ||
    result?.fragments ||
    [];

  const relationships =
    analysis.relationships ||
    result?.relationships ||
    [];


  const confidence =
    Number(
      analysis.reconstruction_confidence ||
        0
    );

  const confidencePercent =
    Math.round(
      confidence * 100
    );


  const priorityScore =
    Number(
      analysis.priority_score ||
        0
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
              item.relationship_probability ||
                0
            ) >= 0.8
        ).length
    );


  const reconstructedCount =
    Number(
      analysis.reconstruction_fragment_count ||
        0
    );


  return (

    <div className="scan-result">

      {/* =================================================
          RESULT HEADER
      ================================================= */}

      <div className="result-header">

        <div>

          <p className="eyebrow">
            ANALYSIS COMPLETE
          </p>

          <h2>
            {file.name ||
              "Recovered Dataset"}
          </h2>

          <p>
            ReFrag AI completed the
            forensic scan using
            fragment classification,
            relationship analysis,
            reconstruction, and
            integrity validation.
          </p>

        </div>


        <div
          className={`result-status status-${String(
            analysis.integrity ||
              "unknown"
          ).toLowerCase()}`}
        >

          <Activity size={18} />

          {analysis.integrity ||
            "UNKNOWN"}

        </div>

      </div>


      {/* =================================================
          TOP METRICS
      ================================================= */}

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
            Number(
              file.size || 0
            ) / 1024
          ).toFixed(2)} KB`}
        />

        <ResultCard
          label="FRAGMENTS"
          value={
            analysis.fragment_count ??
            0
          }
        />

        <ResultCard
          label="ENTROPY"
          value={
            analysis.entropy !==
            undefined
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
            analysis.priority ||
            "LOW"
          }
        />

      </div>


      {/* =================================================
          ML METRICS
      ================================================= */}

      <div className="result-grid ml-grid">

        <ResultCard
          label="RELATIONSHIPS"
          value={
            relationshipsAnalyzed
          }
        />

        <ResultCard
          label="STRONG LINKS"
          value={
            strongRelationships
          }
        />

        <ResultCard
          label="RECONSTRUCTED"
          value={
            reconstructedCount
          }
        />

        <ResultCard
          label="PRIORITY SCORE"
          value={`${priorityScore.toFixed(
            1
          )}/100`}
        />

      </div>


      {/* =================================================
          CONFIDENCE
      ================================================= */}

      <div className="confidence-section">

        <div className="confidence-header">

          <div>

            <span>
              Reconstruction Confidence
            </span>

            <small>
              Based on ML fragment
              relationship analysis
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


      {/* =================================================
          INTEGRITY
      ================================================= */}

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


      {/* =================================================
          FRAGMENTS
      ================================================= */}

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
              No fragment records
              returned by the ML engine.
            </p>

          </div>

        ) : (

          <div className="fragment-list">

            {fragments.map(
              (
                fragment,
                index
              ) => {

                const classification =
                  Number(
                    fragment.classification_confidence ||
                      0
                  );

                return (

                  <div
                    className="fragment-row"
                    key={
                      fragment.fragment_id ??
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
                        {fragment.offset ??
                          0}
                      </span>

                    </div>


                    <div>

                      <span>
                        Size
                      </span>

                      <strong>
                        {fragment.size ??
                          0}
                        {" B"}
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
                              classification *
                                100
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


      {/* =================================================
          RELATIONSHIPS
      ================================================= */}

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
              No relationship records
              returned.
            </p>

          </div>

        ) : (

          <div className="relationship-list">

            {relationships.map(
              (
                relationship,
                index
              ) => {

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
                  probability >=
                  0.8;

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


      {/* =================================================
          PRIORITY
      ================================================= */}

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
              {priorityScore.toFixed(
                1
              )}
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


      {/* =================================================
          RECOVERY ENGINE
      ================================================= */}

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
              {analysis.fragment_count ??
                0}
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
              Integrity:{" "}
              {analysis.integrity ||
                "UNKNOWN"}
            </span>

          </div>

        </div>

      </div>


      {/* =================================================
          RESET
      ================================================= */}

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