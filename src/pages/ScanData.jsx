import { useState, useRef } from "react";
import {
  Upload,
  Folder,
  File,
  HardDrive,
  FileSearch,
  Cpu,
  Network,
  ShieldCheck,
  Play,
  CheckCircle2,
  AlertCircle,
  Loader2,
  RefreshCw,
  FolderOpen,
  FileText,
  Copy,
} from "lucide-react";
import { uploadForensicDataset } from "../services/api";

function formatBytes(bytes, decimals = 2) {
  if (!bytes || bytes === 0) return "0 Bytes";
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ["Bytes", "KB", "MB", "GB", "TB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + " " + sizes[i];
}

function ScanData() {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [isFolderUpload, setIsFolderUpload] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [error, setError] = useState(null);
  
  const [scanning, setScanning] = useState(false);
  const [analysisStarted, setAnalysisStarted] = useState(false);

  const fileInputRef = useRef(null);
  const folderInputRef = useRef(null);

  const handleFileSelect = (e) => {
    if (!e.target.files || e.target.files.length === 0) return;
    processFiles(e.target.files, false);
  };

  const handleFolderSelect = (e) => {
    if (!e.target.files || e.target.files.length === 0) return;
    processFiles(e.target.files, true);
  };

  const processFiles = (fileList, isFolder) => {
    const arr = Array.from(fileList);
    if (arr.length === 0) {
      setError("The selected input contains no files.");
      return;
    }

    const items = arr.map((f) => ({
      rawFile: f,
      name: f.name,
      relativePath: f.webkitRelativePath || f.name,
      size: f.size,
      type: f.type || "binary/raw-evidence",
    }));

    setSelectedFiles(items);
    setIsFolderUpload(isFolder || items.some((i) => i.relativePath.includes("/")));
    setError(null);
    setUploadResult(null);
    setUploadSuccess(false);
    setAnalysisStarted(false);
  };

  const handleUploadSubmit = async () => {
    if (selectedFiles.length === 0) return;

    setIsUploading(true);
    setError(null);

    try {
      const files = selectedFiles.map((s) => s.rawFile);
      const relativePaths = selectedFiles.map((s) => s.relativePath);

      const caseName = isFolderUpload
        ? `Folder Ingestion (${selectedFiles[0]?.relativePath.split("/")[0] || "Dataset"})`
        : `File Ingestion (${selectedFiles.length} file${selectedFiles.length > 1 ? "s" : ""})`;

      const result = await uploadForensicDataset(files, relativePaths, caseName);

      setUploadResult(result);
      setUploadSuccess(true);
      setIsUploading(false);
    } catch (err) {
      setIsUploading(false);
      setError(err.message || "Failed to ingest forensic dataset.");
    }
  };

  const resetSelection = () => {
    setSelectedFiles([]);
    setIsFolderUpload(false);
    setUploadResult(null);
    setUploadSuccess(false);
    setError(null);
    setAnalysisStarted(false);
    if (fileInputRef.current) fileInputRef.current.value = "";
    if (folderInputRef.current) folderInputRef.current.value = "";
  };

  const totalSize = selectedFiles.reduce((acc, curr) => acc + curr.size, 0);

  const startScan = () => {
    if (!uploadSuccess && selectedFiles.length === 0) return;

    setScanning(true);
    setAnalysisStarted(true);

    setTimeout(() => {
      setScanning(false);
    }, 3000);
  };

  return (
    <section className="scan-page">
      {/* HEADER */}
      <div className="scan-page-header">
        <div>
          <p className="eyebrow">FORENSIC DATA ANALYSIS</p>

          <h1>
            Scan damaged storage.
            <br />
            <span>Find what remains.</span>
          </h1>

          <p>
            Provide a controlled storage image or sample dataset. ReFrag AI
            will identify fragments, analyze relationships, and prepare
            recoverable artifacts for reconstruction.
          </p>
        </div>
      </div>

      {/* UPLOAD CARD */}
      <div className="upload-card">
        <div className="upload-icon">
          {isUploading ? (
            <Loader2 size={25} className="animate-spin" />
          ) : uploadSuccess ? (
            <CheckCircle2 size={25} style={{ color: "#4ade80" }} />
          ) : (
            <Upload size={25} />
          )}
        </div>

        <h2>
          {uploadSuccess
            ? "Dataset Ingested Successfully"
            : selectedFiles.length > 0
            ? isFolderUpload
              ? "Selected Forensic Folder"
              : "Selected Forensic Dataset"
            : "Select forensic data"}
        </h2>

        <p>
          {uploadSuccess
            ? "Artifacts and evidence hashes have been saved to PostgreSQL storage."
            : selectedFiles.length > 0
            ? `Review selected ${selectedFiles.length} file(s) below and confirm ingestion.`
            : "Upload a disk image, raw binary sample, or forensic dataset."}
        </p>

        {/* FILE / FOLDER SELECTION BUTTONS (Hidden when upload is successful or pending) */}
        {!uploadSuccess && (
          <div className="upload-button-group">
            <label className="upload-button">
              <File size={17} />
              Choose File(s)
              <input
                type="file"
                multiple
                hidden
                ref={fileInputRef}
                onChange={handleFileSelect}
              />
            </label>

            <label className="upload-button-secondary">
              <FolderOpen size={17} />
              Choose Folder
              <input
                type="file"
                webkitdirectory=""
                directory=""
                multiple
                hidden
                ref={folderInputRef}
                onChange={handleFolderSelect}
              />
            </label>

            {selectedFiles.length > 0 && (
              <button
                className="upload-button-secondary"
                onClick={resetSelection}
                type="button"
                style={{ color: "#ef4444", borderColor: "rgba(239,68,68,0.3)" }}
              >
                <RefreshCw size={14} /> Clear
              </button>
            )}
          </div>
        )}

        {/* ERROR DISPLAY */}
        {error && (
          <div className="ingestion-error-alert">
            <AlertCircle size={18} />
            <span>{error}</span>
          </div>
        )}

        {/* PRE-UPLOAD DATASET SUMMARY */}
        {selectedFiles.length > 0 && !uploadSuccess && (
          <div className="dataset-summary-card">
            <div className="dataset-summary-header">
              <h4>
                {isFolderUpload ? "Selected forensic folder" : "Selected forensic dataset"}
              </h4>
              <span>
                {selectedFiles.length} {selectedFiles.length === 1 ? "file" : "files"} &bull; Total size: {formatBytes(totalSize)}
              </span>
            </div>

            <div className="file-list-preview">
              {selectedFiles.map((item, idx) => (
                <div key={idx} className="file-item-row">
                  <div className="file-item-info">
                    {item.relativePath.includes("/") ? (
                      <Folder size={14} style={{ color: "#818cf8", flexShrink: 0 }} />
                    ) : (
                      <FileText size={14} style={{ color: "#94a3b8", flexShrink: 0 }} />
                    )}
                    <span className="file-item-path" title={item.relativePath}>
                      ✓ {item.relativePath}
                    </span>
                  </div>

                  <div className="file-item-meta">
                    <span>{item.type || "raw"}</span>
                    <span>{formatBytes(item.size)}</span>
                  </div>
                </div>
              ))}
            </div>

            <button
              className="confirm-upload-btn"
              onClick={handleUploadSubmit}
              disabled={isUploading}
            >
              {isUploading ? (
                <>
                  <Loader2 size={16} className="animate-spin" /> Ingesting Dataset...
                </>
              ) : (
                <>
                  <Upload size={16} /> Upload Dataset
                </>
              )}
            </button>
          </div>
        )}

        {/* POST-UPLOAD INGESTION SUCCESS SUMMARY */}
        {uploadSuccess && uploadResult && (
          <div className="ingestion-success-box">
            <div className="ingestion-success-header">
              <CheckCircle2 size={20} />
              <span>Dataset uploaded successfully</span>
            </div>

            <div className="ingestion-meta-grid">
              <div className="ingestion-meta-item">
                <label>Case ID</label>
                <span className="case-id-badge">{uploadResult.case_id}</span>
              </div>
              <div className="ingestion-meta-item">
                <label>Files Ingested</label>
                <span>{uploadResult.files_uploaded}</span>
              </div>
              <div className="ingestion-meta-item">
                <label>Total Size</label>
                <span>{formatBytes(uploadResult.total_size)}</span>
              </div>
              <div className="ingestion-meta-item">
                <label>Status</label>
                <span style={{ color: "#4ade80", textTransform: "capitalize" }}>
                  {uploadResult.status}
                </span>
              </div>
            </div>

            <div className="dataset-summary-header" style={{ marginBottom: "8px", borderBottom: "none" }}>
              <h4 style={{ fontSize: "11px", color: "#94a3b8" }}>Ingested Artifact Evidence Trail</h4>
              <span>SHA-256 Hashed</span>
            </div>

            <div className="artifacts-scroll-list">
              {uploadResult.artifacts.map((art) => (
                <div key={art.artifact_id} className="artifact-row-ingested">
                  <div style={{ display: "flex", alignItems: "center", gap: "8px", overflow: "hidden" }}>
                    <CheckCircle2 size={13} style={{ color: "#4ade80", flexShrink: 0 }} />
                    <span style={{ color: "#e2e8f0", fontWeight: "500" }}>{art.relative_path}</span>
                    {art.is_duplicate && (
                      <span className="duplicate-tag" title="Exact hash matching existing artifact">
                        Duplicate
                      </span>
                    )}
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                    <span className="hash" title={`SHA-256: ${art.sha256}`}>
                      {art.sha256.substring(0, 10)}...
                    </span>
                    <span style={{ color: "#64748b" }}>{formatBytes(art.size)}</span>
                  </div>
                </div>
              ))}
            </div>

            <div style={{ marginTop: "14px", display: "flex", gap: "10px" }}>
              <button
                onClick={resetSelection}
                className="upload-button-secondary"
                style={{ fontSize: "11px", padding: "8px 14px" }}
              >
                <RefreshCw size={13} /> Upload Another Dataset
              </button>
            </div>
          </div>
        )}
      </div>

      {/* PIPELINE */}
      <div className="scan-section">
        <div className="section-header">
          <div>
            <p className="eyebrow">AI RECOVERY PIPELINE</p>
            <h2>Analysis stages</h2>
          </div>

          <button
            className="scan-button"
            disabled={!uploadSuccess || scanning}
            onClick={startScan}
          >
            <Play size={17} />
            {scanning ? "Scanning..." : "Start Analysis"}
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

          <div className="pipeline-arrow">→</div>

          <PipelineCard
            number="02"
            icon={FileSearch}
            title="Fragment Detection"
            description="Detect file signatures and extract candidate fragments."
          />

          <div className="pipeline-arrow">→</div>

          <PipelineCard
            number="03"
            icon={Network}
            title="AI Relationship"
            description="Analyze relationships between fragmented data."
          />

          <div className="pipeline-arrow">→</div>

          <PipelineCard
            number="04"
            icon={Cpu}
            title="Reconstruction"
            description="Build candidate files from related fragments."
          />

          <div className="pipeline-arrow">→</div>

          <PipelineCard
            number="05"
            icon={ShieldCheck}
            title="Integrity"
            description="Validate structure and recovery confidence."
          />
        </div>
      </div>

      {/* ANALYSIS NOTIFICATION / LIVE PROCESS */}
      {analysisStarted && !scanning && (
        <div className="processing-card" style={{ marginTop: "24px", borderColor: "rgba(124, 92, 255, 0.4)" }}>
          <div className="processing-header">
            <div>
              <p className="eyebrow">FORENSIC DATASET READY</p>
              <h2 style={{ color: "#a78bfa" }}>Dataset ready for forensic analysis.</h2>
              <p style={{ fontSize: "12px", color: "#94a3b8", marginTop: "4px" }}>
                Case <code style={{ color: "#60a5fa" }}>{uploadResult?.case_id}</code> is stored in database. AI recovery pipeline can be triggered in the next phase.
              </p>
            </div>
          </div>
        </div>
      )}

      {scanning && (
        <div className="processing-card">
          <div className="processing-header">
            <div>
              <p className="eyebrow">LIVE PROCESSING</p>
              <h2>ReFrag AI is analyzing the dataset</h2>
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
              <strong>{uploadResult?.files_uploaded || 12}</strong>
              <span>Artifacts loaded</span>
            </div>

            <div>
              <strong>1,823</strong>
              <span>File candidates</span>
            </div>

            <div>
              <strong>847</strong>
              <span>Relationships analyzed</span>
            </div>

            <div>
              <strong>64%</strong>
              <span>Pipeline progress</span>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}

function PipelineCard({
  number,
  icon: Icon,
  title,
  description,
  active = false,
}) {
  return (
    <div className={`pipeline-card ${active ? "pipeline-active" : ""}`}>
      <div className="pipeline-number">{number}</div>

      <div className="pipeline-icon">
        <Icon size={21} />
      </div>

      <h3>{title}</h3>

      <p>{description}</p>
    </div>
  );
}

export default ScanData;