import {
  Activity,
  Database,
  FileCheck2,
  AlertTriangle,
  BrainCircuit,
  TrendingUp,
} from "lucide-react";

function Analytics() {
  return (
    <section className="analytics-page">

      {/* HEADER */}

      <div className="analytics-header">
        <div>
          <p className="eyebrow">RECOVERY INTELLIGENCE</p>

          <h1>
            Analyze the recovery.
            <br />
            <span>See the bigger picture.</span>
          </h1>

          <p>
            Monitor fragment discovery, reconstruction results,
            integrity levels, and AI-assisted relationship analysis.
          </p>
        </div>

        <div className="analytics-period">
          <Activity size={15} />
          Current Scan
        </div>
      </div>


      {/* KPI CARDS */}

      <div className="analytics-kpis">

        <Kpi
          icon={Database}
          label="Fragments Processed"
          value="12,482"
          change="+18.4%"
        />

        <Kpi
          icon={FileCheck2}
          label="Files Reconstructed"
          value="1,146"
          change="+12.7%"
        />

        <Kpi
          icon={BrainCircuit}
          label="AI Relationships"
          value="8,742"
          change="+24.2%"
        />

        <Kpi
          icon={AlertTriangle}
          label="Corrupted Regions"
          value="421"
          change="-8.6%"
        />

      </div>


      {/* MAIN ANALYTICS */}

      <div className="analytics-grid">

        {/* RECOVERY DISTRIBUTION */}

        <div className="analytics-card recovery-chart">

          <div className="analytics-card-header">
            <div>
              <p className="eyebrow">RECOVERY STATUS</p>
              <h2>Artifact distribution</h2>
            </div>

            <TrendingUp size={17} />
          </div>


          <div className="distribution">

            <div className="distribution-ring">
              <div>
                <strong>86%</strong>
                <span>Validated</span>
              </div>
            </div>


            <div className="distribution-list">

              <Distribution
                label="Successfully Reconstructed"
                value="1,146"
                percentage="68%"
                type="success"
              />

              <Distribution
                label="Partial Recovery"
                value="421"
                percentage="24%"
                type="partial"
              />

              <Distribution
                label="Corrupted / Unrecoverable"
                value="256"
                percentage="8%"
                type="danger"
              />

            </div>

          </div>

        </div>


        {/* FILE TYPES */}

        <div className="analytics-card">

          <div className="analytics-card-header">

            <div>
              <p className="eyebrow">FILE CLASSIFICATION</p>
              <h2>Detected file types</h2>
            </div>

          </div>


          <div className="file-types">

            <FileType
              type="JPEG"
              count="642"
              percentage="42%"
            />

            <FileType
              type="PDF"
              count="318"
              percentage="21%"
            />

            <FileType
              type="PNG"
              count="211"
              percentage="14%"
            />

            <FileType
              type="ZIP"
              count="164"
              percentage="11%"
            />

            <FileType
              type="DOCX"
              count="103"
              percentage="7%"
            />

            <FileType
              type="Other"
              count="89"
              percentage="5%"
            />

          </div>

        </div>

      </div>


      {/* AI ANALYSIS */}

      <div className="analytics-card ai-insights">

        <div className="analytics-card-header">

          <div>
            <p className="eyebrow">AI RELATIONSHIP ENGINE</p>
            <h2>Fragment relationship confidence</h2>
          </div>

          <div className="ai-status">
            <span />
            Model Active
          </div>

        </div>


        <div className="confidence-bars">

          <Confidence
            label="High confidence"
            range="90–100%"
            value="74%"
          />

          <Confidence
            label="Medium confidence"
            range="70–89%"
            value="19%"
          />

          <Confidence
            label="Low confidence"
            range="<70%"
            value="7%"
          />

        </div>

      </div>


      {/* PROCESSING PIPELINE */}

      <div className="analytics-card pipeline-analytics">

        <div className="analytics-card-header">

          <div>
            <p className="eyebrow">PROCESSING PIPELINE</p>
            <h2>Current analysis throughput</h2>
          </div>

        </div>


        <div className="throughput">

          <PipelineMetric
            title="Scanned"
            value="12,482"
            width="100%"
          />

          <PipelineMetric
            title="Classified"
            value="9,842"
            width="79%"
          />

          <PipelineMetric
            title="Matched"
            value="8,742"
            width="70%"
          />

          <PipelineMetric
            title="Reconstructed"
            value="1,823"
            width="31%"
          />

          <PipelineMetric
            title="Validated"
            value="1,146"
            width="18%"
          />

        </div>

      </div>

    </section>
  );
}


/* KPI */

function Kpi({
  icon: Icon,
  label,
  value,
  change,
}) {
  return (
    <div className="analytics-kpi">

      <div className="kpi-icon">
        <Icon size={18} />
      </div>

      <span>{label}</span>

      <strong>{value}</strong>

      <small>{change} from previous scan</small>

    </div>
  );
}


/* DISTRIBUTION */

function Distribution({
  label,
  value,
  percentage,
  type,
}) {
  return (
    <div className="distribution-item">

      <div className={`distribution-dot ${type}`} />

      <div>
        <strong>{label}</strong>
        <span>{value} artifacts</span>
      </div>

      <b>{percentage}</b>

    </div>
  );
}


/* FILE TYPE */

function FileType({
  type,
  count,
  percentage,
}) {
  return (
    <div className="file-type">

      <div className="file-type-top">
        <strong>{type}</strong>
        <span>{count}</span>
      </div>

      <div className="file-type-bar">
        <div style={{ width: percentage }} />
      </div>

      <small>{percentage} of detected files</small>

    </div>
  );
}


/* CONFIDENCE */

function Confidence({
  label,
  range,
  value,
}) {
  return (
    <div className="confidence-row">

      <div className="confidence-info">
        <strong>{label}</strong>
        <span>{range}</span>
      </div>

      <div className="confidence-track">
        <div
          className="confidence-fill"
          style={{ width: value }}
        />
      </div>

      <b>{value}</b>

    </div>
  );
}


/* PIPELINE */

function PipelineMetric({
  title,
  value,
  width,
}) {
  return (
    <div className="throughput-item">

      <div className="throughput-header">
        <span>{title}</span>
        <strong>{value}</strong>
      </div>

      <div className="throughput-track">
        <div style={{ width }} />
      </div>

    </div>
  );
}


export default Analytics;