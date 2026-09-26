import {
  BookOpen,
  Database,
  BrainCircuit,
  GitBranch,
  ShieldCheck,
  Image,
  Search,
  Layers3,
  AlertTriangle,
} from "lucide-react";
import "../styles/documentation.css";

const sections = [
  {
    icon: Database,
    number: "01",
    title: "Digital Evidence Recovery",
    text:
      "ReFrag AI scans damaged or fragmented storage data, identifies recoverable fragments, and prepares them for AI-assisted analysis.",
  },
  {
    icon: BrainCircuit,
    number: "02",
    title: "Fragment Classification",
    text:
      "Machine learning classifies raw fragments into supported file categories such as JPEG, PNG, PDF, ZIP and text.",
  },
  {
    icon: GitBranch,
    number: "03",
    title: "Relationship Analysis",
    text:
      "The relationship engine evaluates whether fragments are likely to belong together using byte-level and structural features.",
  },
  {
    icon: Layers3,
    number: "04",
    title: "Reconstruction Engine",
    text:
      "High-confidence relationships are used to construct candidate evidence chains from fragmented data.",
  },
  {
    icon: ShieldCheck,
    number: "05",
    title: "Integrity Analysis",
    text:
      "Reconstructed candidates are checked for structural signatures and integrity indicators before being classified as evidence.",
  },
  {
    icon: Search,
    number: "06",
    title: "Evidence Prioritization",
    text:
      "Evidence candidates are prioritized using integrity, reconstruction confidence and fragment-chain support.",
  },
  {
    icon: Image,
    number: "07",
    title: "Visual Image Recovery",
    text:
      "A broken image can be compared against a controlled reference database to identify a visually similar source.",
  },
  {
    icon: AlertTriangle,
    number: "08",
    title: "Evidence Classification",
    text:
      "ReFrag distinguishes directly supported input evidence from reference-assisted restoration and uncertain regions.",
  },
];

function Documentation() {
  return (
    <main className="documentation-page">

      <section className="documentation-hero">
        <div>
          <p className="eyebrow">SYSTEM // DOCUMENTATION</p>
          <h1>ReFrag AI Documentation</h1>
          <p>
            Technical overview of the AI-assisted digital evidence recovery
            pipeline.
          </p>
        </div>

        <div className="docs-badge">
          <BookOpen size={18} />
          <span>TECHNICAL REFERENCE</span>
        </div>
      </section>

      <section className="docs-overview">
        <div className="docs-overview-label">
          <span>REFRAG AI</span>
          <strong>RECOVERY PIPELINE</strong>
        </div>

        <div className="docs-pipeline">
          <span>DAMAGED DATA</span>
          <b>→</b>
          <span>FRAGMENTS</span>
          <b>→</b>
          <span>AI ANALYSIS</span>
          <b>→</b>
          <span>RECONSTRUCTION</span>
          <b>→</b>
          <span>EVIDENCE</span>
        </div>
      </section>

      <section className="docs-section">
        <div className="docs-section-title">
          <p className="eyebrow">CORE SYSTEM</p>
          <h2>How ReFrag AI Works</h2>
        </div>

        <div className="docs-grid">
          {sections.map((section) => {
            const Icon = section.icon;

            return (
              <article className="docs-card" key={section.number}>
                <div className="docs-card-top">
                  <span>{section.number}</span>
                  <Icon size={18} />
                </div>

                <h3>{section.title}</h3>

                <p>{section.text}</p>

                <div className="docs-card-line" />
              </article>
            );
          })}
        </div>
      </section>

      <section className="docs-section">
        <div className="docs-section-title">
          <p className="eyebrow">VISUAL RECOVERY</p>
          <h2>Reference-Assisted Image Analysis</h2>
        </div>

        <div className="docs-visual-flow">
          <div>
            <strong>01</strong>
            <span>Broken Image</span>
          </div>

          <b>→</b>

          <div>
            <strong>02</strong>
            <span>Visual Features</span>
          </div>

          <b>→</b>

          <div>
            <strong>03</strong>
            <span>Reference Search</span>
          </div>

          <b>→</b>

          <div>
            <strong>04</strong>
            <span>Damage Analysis</span>
          </div>

          <b>→</b>

          <div>
            <strong>05</strong>
            <span>Restoration</span>
          </div>
        </div>
      </section>

      <section className="docs-evidence-model">
        <div>
          <p className="eyebrow">FORENSIC MODEL</p>
          <h2>Evidence States</h2>
        </div>

        <div className="evidence-state">
          <span className="state-dot recovered" />
          <div>
            <strong>RECOVERED</strong>
            <p>Directly supported by the available input evidence.</p>
          </div>
        </div>

        <div className="evidence-state">
          <span className="state-dot restored" />
          <div>
            <strong>RESTORED</strong>
            <p>Generated or reconstructed using reference-assisted analysis.</p>
          </div>
        </div>

        <div className="evidence-state">
          <span className="state-dot unknown" />
          <div>
            <strong>UNKNOWN</strong>
            <p>Insufficient evidence to establish the missing information.</p>
          </div>
        </div>
      </section>

      <section className="docs-limitations">
        <AlertTriangle size={18} />

        <div>
          <strong>Important: Prototype Limitations</strong>
          <p>
            ReFrag AI is a hackathon prototype. Synthetic datasets and
            reference-assisted visual recovery are used for demonstration.
            Real-world forensic recovery requires validation against authentic
            damaged storage media and appropriate forensic procedures.
          </p>
        </div>
      </section>

      <footer className="docs-footer">
        ReFrag AI // AI-Assisted Intelligent Data Recovery & Digital Evidence
        Reconstruction
      </footer>

    </main>
  );
}

export default Documentation;