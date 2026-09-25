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
} from "lucide-react";

function ScanData() {
  const [file, setFile] = useState(null);
  const [scanning, setScanning] = useState(false);

  const startScan = () => {
    if (!file) return;

    setScanning(true);

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
            Provide a controlled storage image or sample dataset.
            ReFrag AI will identify fragments, analyze relationships,
            and prepare recoverable artifacts for reconstruction.
          </p>
        </div>
      </div>


      {/* UPLOAD */}

      <div className="upload-card">

        <div className="upload-icon">
          <Upload size={25} />
        </div>

        <h2>
          {file ? file.name : "Select forensic data"}
        </h2>

        <p>
          Upload a disk image, raw binary sample, or forensic dataset.
        </p>

        <label className="upload-button">
          <Upload size={17} />
          Choose File

          <input
            type="file"
            hidden
            onChange={(e) => setFile(e.target.files[0])}
          />
        </label>

        {file && (
          <div className="selected-file">
            <HardDrive size={16} />

            <div>
              <strong>{file.name}</strong>
              <span>
                {(file.size / 1024 / 1024).toFixed(2)} MB
              </span>
            </div>

            <CheckCircle2 size={17} />
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
            disabled={!file || scanning}
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


      {/* LIVE PROCESS */}

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
              <strong>12,482</strong>
              <span>Fragments scanned</span>
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

      <div className="pipeline-number">
        {number}
      </div>

      <div className="pipeline-icon">
        <Icon size={21} />
      </div>

      <h3>{title}</h3>

      <p>{description}</p>

    </div>
  );
}

export default ScanData;