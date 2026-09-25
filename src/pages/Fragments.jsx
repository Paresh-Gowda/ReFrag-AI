import {
  Database,
  BrainCircuit,
  Link2,
  FileImage,
  FileText,
  Archive,
  CheckCircle2,
  AlertTriangle,
} from "lucide-react";

function Fragments() {
  return (
    <section className="fragments-page">

      {/* HEADER */}

      <div className="fragments-header">
        <div>
          <p className="eyebrow">FRAGMENT INTELLIGENCE</p>

          <h1>
            Understand the pieces.
            <br />
            <span>Reconstruct the whole.</span>
          </h1>

          <p>
            ReFrag AI analyzes isolated data fragments and determines
            which fragments are likely to belong together.
          </p>
        </div>

        <div className="fragment-count">
          <Database size={17} />
          <div>
            <strong>12,482</strong>
            <span>Fragments detected</span>
          </div>
        </div>
      </div>


      {/* ANALYSIS PIPELINE */}

      <div className="fragment-flow">

        <div className="flow-title">
          <p className="eyebrow">RECONSTRUCTION FLOW</p>
          <h2>Fragment relationship analysis</h2>
        </div>

        <div className="fragment-workspace">

          {/* RAW FRAGMENTS */}

          <div className="fragment-column">

            <div className="column-header">
              <Database size={16} />
              <span>RAW FRAGMENTS</span>
            </div>

            <FragmentCard
              id="F-001"
              type="JPEG"
              size="64 KB"
              icon={FileImage}
            />

            <FragmentCard
              id="F-002"
              type="JPEG"
              size="64 KB"
              icon={FileImage}
              warning
            />

            <FragmentCard
              id="F-003"
              type="JPEG"
              size="64 KB"
              icon={FileImage}
            />

            <FragmentCard
              id="F-004"
              type="JPEG"
              size="64 KB"
              icon={FileImage}
            />

          </div>


          {/* AI */}

          <div className="ai-analysis">

            <div className="ai-orb">
              <BrainCircuit size={25} />
            </div>

            <strong>AI RELATIONSHIP</strong>

            <span>
              Analyzing fragment
              <br />
              compatibility
            </span>

            <div className="confidence">
              94.7%
              <small>confidence</small>
            </div>

          </div>


          {/* RECONSTRUCTION */}

          <div className="fragment-column">

            <div className="column-header">
              <Link2 size={16} />
              <span>CANDIDATE CHAIN</span>
            </div>

            <div className="chain-card">

              <div className="chain-node">
                <span>F-001</span>
              </div>

              <div className="chain-line" />

              <div className="chain-node">
                <span>F-003</span>
              </div>

              <div className="chain-line" />

              <div className="chain-node">
                <span>F-004</span>
              </div>

              <div className="chain-line" />

              <div className="chain-node">
                <span>F-008</span>
              </div>

            </div>

            <div className="reconstruction-result">

              <FileImage size={20} />

              <div>
                <strong>IMG_2048.jpg</strong>
                <span>Candidate reconstruction</span>
              </div>

              <CheckCircle2 size={18} />

            </div>

          </div>

        </div>

      </div>


      {/* FRAGMENT TABLE */}

      <div className="fragment-section">

        <div className="section-header">
          <div>
            <p className="eyebrow">FRAGMENT INVENTORY</p>
            <h2>Detected fragments</h2>
          </div>
        </div>

        <div className="fragment-table">

          <div className="fragment-table-header">
            <span>Fragment</span>
            <span>Type</span>
            <span>Size</span>
            <span>AI Match</span>
            <span>Condition</span>
          </div>

          <FragmentRow
            id="F-001"
            type="JPEG"
            size="64 KB"
            match="97%"
            condition="Valid"
          />

          <FragmentRow
            id="F-002"
            type="JPEG"
            size="64 KB"
            match="61%"
            condition="Damaged"
            damaged
          />

          <FragmentRow
            id="F-003"
            type="JPEG"
            size="64 KB"
            match="94%"
            condition="Valid"
          />

          <FragmentRow
            id="F-004"
            type="JPEG"
            size="64 KB"
            match="91%"
            condition="Valid"
          />

          <FragmentRow
            id="F-008"
            type="JPEG"
            size="32 KB"
            match="89%"
            condition="Partial"
            partial
          />

        </div>

      </div>

    </section>
  );
}


/* FRAGMENT CARD */

function FragmentCard({
  id,
  type,
  size,
  icon: Icon,
  warning = false,
}) {
  return (
    <div className={`fragment-card ${warning ? "fragment-warning" : ""}`}>

      <div className="fragment-card-icon">
        <Icon size={16} />
      </div>

      <div>
        <strong>{id}</strong>
        <span>{type} · {size}</span>
      </div>

      {warning && (
        <AlertTriangle size={14} />
      )}

    </div>
  );
}


/* TABLE ROW */

function FragmentRow({
  id,
  type,
  size,
  match,
  condition,
  damaged = false,
  partial = false,
}) {
  return (
    <div className="fragment-table-row">

      <strong>{id}</strong>

      <span>{type}</span>

      <span>{size}</span>

      <span className="match-value">
        {match}
      </span>

      <span
        className={`fragment-status ${
          damaged
            ? "damaged"
            : partial
            ? "partial"
            : "valid"
        }`}
      >
        {condition}
      </span>

    </div>
  );
}

export default Fragments;