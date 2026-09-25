import {
  FileImage,
  ShieldCheck,
  BrainCircuit,
  Link2,
  AlertTriangle,
  CheckCircle2,
  Download,
  Eye,
} from "lucide-react";

function Evidence() {
  return (
    <section className="evidence-page">

      {/* HEADER */}

      <div className="evidence-page-header">

        <div>
          <p className="eyebrow">DIGITAL EVIDENCE</p>

          <h1>
            Reconstructed artifact.
            <br />
            <span>Inspect every detail.</span>
          </h1>

          <p>
            Review recovered files, fragment relationships,
            reconstruction confidence, and integrity information.
          </p>
        </div>

        <button className="export-button">
          <Download size={16} />
          Export Report
        </button>

      </div>


      {/* ARTIFACT HEADER */}

      <div className="artifact-banner">

        <div className="artifact-main">

          <div className="artifact-file-icon">
            <FileImage size={25} />
          </div>

          <div>
            <p>RECOVERED ARTIFACT</p>
            <h2>IMG_2048.jpg</h2>
            <span>
              JPEG · 286 KB · Reconstructed from 5 fragments
            </span>
          </div>

        </div>

        <div className="artifact-status">
          <CheckCircle2 size={16} />
          Reconstructed
        </div>

      </div>


      {/* MAIN GRID */}

      <div className="evidence-grid">

        {/* PREVIEW */}

        <div className="evidence-card preview-card">

          <div className="card-header">
            <div>
              <p className="eyebrow">ARTIFACT PREVIEW</p>
              <h3>Recovered image</h3>
            </div>

            <button className="preview-button">
              <Eye size={15} />
              Full View
            </button>
          </div>

          <div className="image-preview">

            <div className="preview-image">
              <div className="image-placeholder">
                <FileImage size={42} />
                <span>Recovered Image Preview</span>
                <small>IMG_2048.jpg</small>
              </div>
            </div>

          </div>

        </div>


        {/* METRICS */}

        <div className="evidence-card metrics-card">

          <div className="card-header">
            <div>
              <p className="eyebrow">RECOVERY METRICS</p>
              <h3>Artifact confidence</h3>
            </div>
          </div>

          <Metric
            label="Integrity"
            value="92%"
            description="Structural validation"
          />

          <Metric
            label="AI Confidence"
            value="95%"
            description="Fragment relationship confidence"
          />

          <Metric
            label="Reconstruction"
            value="89%"
            description="Estimated completeness"
          />

          <Metric
            label="Fragments"
            value="5 / 6"
            description="Fragments successfully linked"
          />

        </div>

      </div>


      {/* INTEGRITY MAP */}

      <div className="evidence-card integrity-card">

        <div className="card-header">

          <div>
            <p className="eyebrow">INTEGRITY ANALYSIS</p>
            <h3>Artifact structure</h3>
          </div>

          <div className="integrity-legend">
            <span className="legend-valid" />
            Valid
            <span className="legend-partial" />
            Partial
            <span className="legend-corrupt" />
            Corrupt
          </div>

        </div>

        <div className="integrity-map">

          <div className="integrity-block valid">
            Header
          </div>

          <div className="integrity-block valid">
            Metadata
          </div>

          <div className="integrity-block valid large">
            Image Data
          </div>

          <div className="integrity-block partial">
            Missing
          </div>

          <div className="integrity-block valid">
            Footer
          </div>

        </div>

        <div className="integrity-summary">

          <CheckCircle2 size={17} />

          <div>
            <strong>Structure successfully validated</strong>
            <span>
              One incomplete region was detected in the image data.
            </span>
          </div>

        </div>

      </div>


      {/* LOWER GRID */}

      <div className="evidence-grid">

        {/* FRAGMENT CHAIN */}

        <div className="evidence-card">

          <div className="card-header">

            <div>
              <p className="eyebrow">RECONSTRUCTION</p>
              <h3>Fragment relationship</h3>
            </div>

            <Link2 size={17} />

          </div>

          <div className="evidence-chain">

            <ChainNode id="F-001" confidence="97%" />
            <ChainConnector />
            <ChainNode id="F-003" confidence="94%" />
            <ChainConnector />
            <ChainNode id="F-004" confidence="91%" />
            <ChainConnector />
            <ChainNode id="F-008" confidence="89%" />

          </div>

          <div className="chain-note">
            <BrainCircuit size={16} />

            <span>
              AI identified these fragments as a probable
              reconstruction sequence.
            </span>
          </div>

        </div>


        {/* ISSUES */}

        <div className="evidence-card">

          <div className="card-header">

            <div>
              <p className="eyebrow">ANOMALIES</p>
              <h3>Detected issues</h3>
            </div>

            <AlertTriangle size={17} />

          </div>

          <div className="issue">

            <div className="issue-icon warning">
              <AlertTriangle size={15} />
            </div>

            <div>
              <strong>Missing fragment</strong>
              <span>
                Expected fragment F-007 was not recovered.
              </span>
            </div>

          </div>

          <div className="issue">

            <div className="issue-icon success">
              <CheckCircle2 size={15} />
            </div>

            <div>
              <strong>File structure valid</strong>
              <span>
                JPEG header and footer successfully validated.
              </span>
            </div>

          </div>

        </div>

      </div>


      {/* RECONSTRUCTION DETAILS */}

      <div className="evidence-card reconstruction-details">

        <div className="card-header">
          <div>
            <p className="eyebrow">ANALYSIS DETAILS</p>
            <h3>Reconstruction summary</h3>
          </div>
        </div>

        <div className="detail-grid">

          <Detail label="Original fragments" value="6" />
          <Detail label="Recovered fragments" value="5" />
          <Detail label="Missing fragments" value="1" />
          <Detail label="Detected file type" value="JPEG" />
          <Detail label="Integrity score" value="92%" />
          <Detail label="AI confidence" value="95%" />

        </div>

      </div>

    </section>
  );
}


function Metric({ label, value, description }) {
  return (
    <div className="metric">

      <div>
        <span>{label}</span>
        <small>{description}</small>
      </div>

      <strong>{value}</strong>

    </div>
  );
}


function ChainNode({ id, confidence }) {
  return (
    <div className="chain-node-large">

      <strong>{id}</strong>

      <span>{confidence}</span>

    </div>
  );
}


function ChainConnector() {
  return (
    <div className="chain-connector">
      <div />
      <span>AI</span>
      <div />
    </div>
  );
}


function Detail({ label, value }) {
  return (
    <div className="detail-item">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}


export default Evidence;