import { useEffect, useMemo, useState } from "react";
import {
  Database,
  Search,
  FileCode2,
  Activity,
  AlertCircle,
  Brain,
  Network,
  ShieldCheck,
  Layers3,
  ChevronRight,
  Zap,
  RefreshCw,
  Image as ImageIcon,
  Target,
  ScanSearch,
  ShieldAlert,
  CheckCircle2,
  Eye,
  Sparkles,
  Map,
  RotateCcw,
} from "lucide-react";

import { getFragments } from "../services/api";
import "../styles/fragments.css";

function formatConfidence(value) {
  const number = Number(value);

  if (!Number.isFinite(number)) {
    return "—";
  }

  const normalized = number <= 1 ? number * 100 : number;

  return `${normalized.toFixed(1)}%`;
}

function formatNumber(value) {
  const number = Number(value);

  if (!Number.isFinite(number)) {
    return "—";
  }

  return number.toLocaleString();
}

function formatPercent(value) {
  const number = Number(value);

  if (!Number.isFinite(number)) {
    return "—";
  }

  return `${number.toFixed(2)}%`;
}

function getOutputUrl(path) {
  if (!path) return "";

  if (path.startsWith("http://") || path.startsWith("https://")) {
    return path;
  }

  if (path.startsWith("/api/")) {
    return `http://localhost:8000${path}`;
  }

  return path;
}

function VisualMetric({
  icon,
  label,
  value,
  description,
  className = "",
}) {
  return (
    <div className={`metric-card visual-metric ${className}`}>
      <div className="metric-icon">{icon}</div>

      <div>
        <span>{label}</span>

        <strong>{value}</strong>

        <small>{description}</small>
      </div>
    </div>
  );
}

function VisualPipelineStep({
  number,
  icon,
  title,
  description,
  active = false,
}) {
  return (
    <div className={`visual-pipeline-step ${active ? "active" : ""}`}>
      <div className="pipeline-number">{number}</div>

      <div className="pipeline-icon">{icon}</div>

      <div className="pipeline-copy">
        <strong>{title}</strong>
        <span>{description}</span>
      </div>
    </div>
  );
}

function VisualRecoveryView({
  data,
  activeFile,
  loadFragments,
  refreshing,
}) {
  const reference =
    data?.reference ||
    data?.reference_image ||
    data?.matched_reference ||
    null;

  const similarity = Number(
    data?.similarity ??
      data?.similarity_percent ??
      data?.reference_similarity ??
      0
  );

  const recovered = Number(
    data?.recovered_percentage ??
      data?.recovered_percent ??
      0
  );

  const damaged = Number(
    data?.damaged_percentage ??
      data?.damaged_percent ??
      0
  );

  const damageRegions = Number(
    data?.damage_regions ?? 0
  );

  const outputs = data?.outputs || {};

  const referenceImage =
    outputs.reference_image ||
    outputs.reference ||
    data?.reference_output ||
    "";

  const damageMask =
    outputs.damage_mask ||
    data?.damage_mask ||
    "";

  const evidenceMap =
    outputs.evidence_map ||
    data?.evidence_map ||
    "";

  const restoredImage =
    outputs.restored_image ||
    data?.restored_image ||
    "";

  const displayReference =
    typeof reference === "string"
      ? reference.split(/[\\/]/).pop()
      : reference?.filename ||
        reference?.file ||
        "Reference unavailable";

  const modeLabel = "VISUAL EVIDENCE MODE";

  return (
    <div className="visual-recovery-page">
      {/* ================================================= */}
      {/* VISUAL HERO */}
      {/* ================================================= */}

      <section className="fragments-hero visual-hero">
        <div className="hero-copy">
          <div className="live-label">
            <span className="live-dot" />
            {modeLabel}
          </div>

          <p className="eyebrow">
            VISUAL RECOVERY INTELLIGENCE
          </p>

          <h1>Image Evidence Analysis</h1>

          <p className="hero-description">
            Analyze a damaged image through visual similarity,
            reference matching, damage localization and
            reference-assisted reconstruction.
          </p>

          <div className="active-file">
            <ImageIcon size={15} />

            <span>ACTIVE EVIDENCE</span>

            <strong>{activeFile}</strong>
          </div>
        </div>

        <div className="hero-actions">
          <div className="fragment-count visual-count">
            <ImageIcon size={18} />

            <div>
              <strong>VISUAL</strong>
              <span>recovery session</span>
            </div>
          </div>

          <button
            className="refresh-button"
            type="button"
            onClick={() => loadFragments(true)}
            disabled={refreshing}
          >
            <RefreshCw
              size={16}
              className={refreshing ? "spin" : ""}
            />

            {refreshing ? "Refreshing" : "Refresh"}
          </button>
        </div>
      </section>

      {/* ================================================= */}
      {/* VISUAL METRICS */}
      {/* ================================================= */}

      <section className="fragment-metrics visual-metrics">
        <VisualMetric
          icon={<Target size={18} />}
          label="REFERENCE SIMILARITY"
          value={formatPercent(similarity)}
          description="Best visual database match"
        />

        <VisualMetric
          icon={<CheckCircle2 size={18} />}
          label="RECOVERED"
          value={formatPercent(recovered)}
          description="Pixels supported by recovery analysis"
        />

        <VisualMetric
          icon={<ShieldAlert size={18} />}
          label="DAMAGED"
          value={formatPercent(damaged)}
          description="Pixels requiring restoration"
        />

        <VisualMetric
          icon={<Map size={18} />}
          label="DAMAGE REGIONS"
          value={formatNumber(damageRegions)}
          description="Detected affected regions"
        />
      </section>

      {/* ================================================= */}
      {/* REFERENCE MATCH */}
      {/* ================================================= */}

      <section className="visual-reference-section">
        <div className="section-heading">
          <div>
            <p className="eyebrow">
              REFERENCE DATABASE SEARCH
            </p>

            <h2>Matched Reference</h2>

            <p>
              The recovery engine compares visual features
              against the available reference database and
              selects the strongest match.
            </p>
          </div>

          <div className="relationship-badge">
            <Target size={15} />
            {formatPercent(similarity)} match
          </div>
        </div>

        <div className="visual-reference-card">
          <div className="reference-preview">
            {referenceImage ? (
              <img
                src={getOutputUrl(referenceImage)}
                alt="Matched reference"
              />
            ) : (
              <div className="visual-image-placeholder">
                <ImageIcon size={34} />
                <span>Reference image unavailable</span>
              </div>
            )}
          </div>

          <div className="reference-details">
            <div className="reference-status">
              <span className="status-dot" />
              REFERENCE MATCH FOUND
            </div>

            <h3>{displayReference}</h3>

            <p>
              Highest-scoring visual reference identified
              for the current evidence image.
            </p>

            <div className="reference-score">
              <div className="score-heading">
                <span>Visual similarity</span>
                <strong>{formatPercent(similarity)}</strong>
              </div>

              <div className="confidence-track">
                <span
                  style={{
                    width: `${Math.min(
                      100,
                      Math.max(0, similarity)
                    )}%`,
                  }}
                />
              </div>
            </div>

            <div className="reference-note">
              <ShieldCheck size={17} />

              <div>
                <strong>Forensic interpretation</strong>

                <p>
                  Similarity indicates visual correspondence
                  with the reference database. It does not
                  independently establish authenticity or
                  provenance.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ================================================= */}
      {/* VISUAL PIPELINE */}
      {/* ================================================= */}

      <section className="visual-pipeline-section">
        <div className="section-heading">
          <div>
            <p className="eyebrow">
              RECOVERY PIPELINE
            </p>

            <h2>Visual Analysis Process</h2>

            <p>
              The current image is processed through a
              sequence of visual evidence analysis stages.
            </p>
          </div>
        </div>

        <div className="visual-pipeline">
          <VisualPipelineStep
            number="01"
            icon={<ImageIcon size={18} />}
            title="Input Image"
            description="Damaged evidence uploaded"
            active
          />

          <ChevronRight className="pipeline-arrow" size={18} />

          <VisualPipelineStep
            number="02"
            icon={<ScanSearch size={18} />}
            title="Feature Extraction"
            description="Color, structure and edge signals"
            active
          />

          <ChevronRight className="pipeline-arrow" size={18} />

          <VisualPipelineStep
            number="03"
            icon={<Target size={18} />}
            title="Reference Matching"
            description="Reference database comparison"
            active
          />

          <ChevronRight className="pipeline-arrow" size={18} />

          <VisualPipelineStep
            number="04"
            icon={<Map size={18} />}
            title="Damage Analysis"
            description="Affected regions localized"
            active
          />

          <ChevronRight className="pipeline-arrow" size={18} />

          <VisualPipelineStep
            number="05"
            icon={<Sparkles size={18} />}
            title="Restoration"
            description="Reference-assisted reconstruction"
            active
          />
        </div>
      </section>

      {/* ================================================= */}
      {/* VISUAL OUTPUTS */}
      {/* ================================================= */}

      <section className="visual-output-section">
        <div className="section-heading">
          <div>
            <p className="eyebrow">
              EVIDENCE OUTPUTS
            </p>

            <h2>Recovery Artifacts</h2>

            <p>
              Generated artifacts from the current visual
              recovery session.
            </p>
          </div>
        </div>

        <div className="visual-output-grid">
          <div className="visual-output-card">
            <div className="output-card-header">
              <div>
                <ImageIcon size={17} />
                <span>REFERENCE</span>
              </div>

              <span className="output-tag">
                MATCHED
              </span>
            </div>

            <div className="output-image">
              {referenceImage ? (
                <img
                  src={getOutputUrl(referenceImage)}
                  alt="Reference output"
                />
              ) : (
                <div className="visual-image-placeholder">
                  <ImageIcon size={28} />
                  <span>No reference output</span>
                </div>
              )}
            </div>
          </div>

          <div className="visual-output-card">
            <div className="output-card-header">
              <div>
                <Map size={17} />
                <span>DAMAGE MASK</span>
              </div>

              <span className="output-tag">
                ANALYSIS
              </span>
            </div>

            <div className="output-image">
              {damageMask ? (
                <img
                  src={getOutputUrl(damageMask)}
                  alt="Damage mask"
                />
              ) : (
                <div className="visual-image-placeholder">
                  <Map size={28} />
                  <span>No damage mask</span>
                </div>
              )}
            </div>
          </div>

          <div className="visual-output-card">
            <div className="output-card-header">
              <div>
                <Eye size={17} />
                <span>EVIDENCE MAP</span>
              </div>

              <span className="output-tag">
                EVIDENCE
              </span>
            </div>

            <div className="output-image">
              {evidenceMap ? (
                <img
                  src={getOutputUrl(evidenceMap)}
                  alt="Evidence map"
                />
              ) : (
                <div className="visual-image-placeholder">
                  <Eye size={28} />
                  <span>No evidence map</span>
                </div>
              )}
            </div>
          </div>

          <div className="visual-output-card">
            <div className="output-card-header">
              <div>
                <RotateCcw size={17} />
                <span>RESTORED IMAGE</span>
              </div>

              <span className="output-tag">
                ASSISTED
              </span>
            </div>

            <div className="output-image">
              {restoredImage ? (
                <img
                  src={getOutputUrl(restoredImage)}
                  alt="Restored image"
                />
              ) : (
                <div className="visual-image-placeholder">
                  <RotateCcw size={28} />
                  <span>No restored output</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* ================================================= */}
      {/* FORENSIC EVIDENCE NOTE */}
      {/* ================================================= */}

      <section className="visual-evidence-note">
        <ShieldCheck size={20} />

        <div>
          <strong>Evidence classification</strong>

          <p>
            Preserved pixels represent direct input evidence.
            Damage regions represent differences identified
            through the reference-assisted analysis. Restored
            pixels are reference-assisted and should be
            distinguished from directly recovered evidence.
          </p>
        </div>
      </section>
    </div>
  );
}

function Fragments() {
  const [data, setData] = useState(null);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");
  const [selectedFragment, setSelectedFragment] =
    useState(null);

  async function loadFragments(showRefresh = false) {
    try {
      if (showRefresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }

      setError("");

      const response = await getFragments();

      setData(response || {});
    } catch (error) {
      console.error(
        "Failed to load fragment intelligence:",
        error
      );

      setError(
        error.message ||
          "Failed to load fragment intelligence."
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }

  useEffect(() => {
    loadFragments();
  }, []);

  const mode =
    String(data?.mode || "forensic").toLowerCase();

  const isVisual =
    mode === "visual" ||
    data?.visual_recovery === true;

  const fragments = Array.isArray(data?.fragments)
    ? data.fragments
    : [];

  const relationships = Array.isArray(
    data?.relationships
  )
    ? data.relationships
    : [];

  const filteredFragments = useMemo(() => {
    const query = search.toLowerCase().trim();

    if (!query) {
      return fragments;
    }

    return fragments.filter((fragment) =>
      Object.values(fragment).some((value) =>
        String(value)
          .toLowerCase()
          .includes(query)
      )
    );
  }, [fragments, search]);

  const fileType =
    data?.file_type || "UNKNOWN";

  const entropy = Number(data?.entropy);

  const relationshipsAnalyzed = Number(
    data?.relationships_analyzed || 0
  );

  const strongRelationships = Number(
    data?.strong_relationships || 0
  );

  const activeFile =
    data?.file || "No active scan";

  if (loading) {
    return (
      <div className="fragments-page">
        <div className="fragments-loading">
          <div className="loading-orbit">
            <Database size={24} />
          </div>

          <strong>
            Loading fragment intelligence
          </strong>

          <span>
            Reading the latest forensic scan...
          </span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="fragments-page">
        <div className="fragments-error">
          <AlertCircle size={22} />

          <div>
            <strong>
              Unable to load fragment intelligence
            </strong>

            <p>{error}</p>

            <button
              type="button"
              onClick={() => loadFragments(true)}
            >
              <RefreshCw size={15} />
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (isVisual) {
    return (
      <div className="fragments-page">
        <VisualRecoveryView
          data={data}
          activeFile={activeFile}
          loadFragments={loadFragments}
          refreshing={refreshing}
        />
      </div>
    );
  }

  return (
    <div className="fragments-page">

      {/* ================================================= */}
      {/* FORENSIC HEADER */}
      {/* ================================================= */}

      <section className="fragments-hero">
        <div className="hero-copy">
          <div className="live-label">
            <span className="live-dot" />
            LIVE FORENSIC ANALYSIS
          </div>

          <p className="eyebrow">
            FRAGMENT INTELLIGENCE
          </p>

          <h1>Storage Fragments</h1>

          <p className="hero-description">
            Inspect recovered storage fragments, AI
            classifications and learned relationships
            from the latest scan.
          </p>

          <div className="active-file">
            <FileCode2 size={15} />

            <span>ACTIVE EVIDENCE</span>

            <strong>{activeFile}</strong>
          </div>
        </div>

        <div className="hero-actions">
          <div className="fragment-count">
            <Database size={18} />

            <div>
              <strong>
                {formatNumber(fragments.length)}
              </strong>

              <span>fragments</span>
            </div>
          </div>

          <button
            className="refresh-button"
            type="button"
            onClick={() => loadFragments(true)}
            disabled={refreshing}
          >
            <RefreshCw
              size={16}
              className={
                refreshing ? "spin" : ""
              }
            />

            {refreshing
              ? "Refreshing"
              : "Refresh"}
          </button>
        </div>
      </section>

      {/* ================================================= */}
      {/* METRICS */}
      {/* ================================================= */}

      <section className="fragment-metrics">

        <div className="metric-card">
          <div className="metric-icon">
            <Layers3 size={18} />
          </div>

          <div>
            <span>FRAGMENTS DETECTED</span>

            <strong>
              {formatNumber(
                fragments.length
              )}
            </strong>

            <small>From current scan</small>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">
            <Brain size={18} />
          </div>

          <div>
            <span>FILE CLASSIFICATION</span>

            <strong>
              {String(
                fileType
              ).toUpperCase()}
            </strong>

            <small>
              AI fragment analysis
            </small>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">
            <Activity size={18} />
          </div>

          <div>
            <span>GLOBAL ENTROPY</span>

            <strong>
              {Number.isFinite(entropy)
                ? entropy.toFixed(3)
                : "—"}
            </strong>

            <small>
              Byte distribution signal
            </small>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">
            <Network size={18} />
          </div>

          <div>
            <span>STRONG RELATIONSHIPS</span>

            <strong>
              {formatNumber(
                strongRelationships
              )}
            </strong>

            <small>
              {formatNumber(
                relationshipsAnalyzed
              )}{" "}
              relationships analyzed
            </small>
          </div>
        </div>

      </section>

      {/* ================================================= */}
      {/* SEARCH */}
      {/* ================================================= */}

      <section className="fragment-toolbar">

        <div className="toolbar-title">
          <div className="toolbar-icon">
            <Search size={16} />
          </div>

          <div>
            <strong>
              Fragment Explorer
            </strong>

            <span>
              Search the current evidence set
            </span>
          </div>
        </div>

        <div className="fragment-search">
          <Search size={16} />

          <input
            type="text"
            placeholder="Search ID, type, source, index..."
            value={search}
            onChange={(event) =>
              setSearch(event.target.value)
            }
          />

          {search && (
            <button
              type="button"
              onClick={() => setSearch("")}
              className="clear-search"
            >
              ×
            </button>
          )}
        </div>

        <div className="result-count">
          {filteredFragments.length}
          {" / "}
          {fragments.length}
        </div>

      </section>

      {/* ================================================= */}
      {/* FRAGMENT TABLE */}
      {/* ================================================= */}

      <section className="fragment-table-card">

        <div className="table-heading">

          <div>
            <p className="eyebrow">
              RAW FRAGMENT INTELLIGENCE
            </p>

            <h2>Extracted Fragments</h2>
          </div>

          <div className="table-status">
            <span className="status-dot" />
            LIVE DATA
          </div>

        </div>

        <div className="fragments-table-wrapper">

          <table className="fragments-table">

            <thead>
              <tr>
                <th>FRAGMENT</th>
                <th>TYPE</th>
                <th>INDEX</th>
                <th>SIZE</th>
                <th>ENTROPY</th>
                <th>AI CONFIDENCE</th>
                <th />
              </tr>
            </thead>

            <tbody>
              {filteredFragments.map(
                (fragment, index) => {

                  const fragmentId =
                    fragment.fragment_id ||
                    fragment.id ||
                    fragment.fragment ||
                    `FRAG_${String(
                      index + 1
                    ).padStart(6, "0")}`;

                  const type =
                    fragment.file_type ||
                    fragment.type ||
                    fileType ||
                    "UNKNOWN";

                  const source =
                    fragment.source_file ||
                    fragment.source ||
                    fragment.source_id ||
                    activeFile;

                  const fragmentIndex =
                    fragment.fragment_index ??
                    fragment.index ??
                    index;

                  const size =
                    fragment.size ??
                    fragment.fragment_size;

                  const fragmentEntropy =
                    fragment.entropy;

                  const confidence =
                    fragment.confidence ??
                    fragment.classification_confidence ??
                    fragment.probability;

                  const isSelected =
                    selectedFragment?.fragment_id ===
                    fragment.fragment_id;

                  return (
                    <tr
                      key={`${fragmentId}-${index}`}
                      className={
                        isSelected
                          ? "selected-row"
                          : ""
                      }
                      onClick={() =>
                        setSelectedFragment(
                          fragment
                        )
                      }
                    >

                      <td>
                        <div className="fragment-id">

                          <div className="fragment-file-icon">
                            <FileCode2 size={15} />
                          </div>

                          <div>
                            <strong>
                              {fragmentId}
                            </strong>

                            <span>
                              {source}
                            </span>
                          </div>

                        </div>
                      </td>

                      <td>
                        <span className="file-type">
                          {String(
                            type
                          ).toUpperCase()}
                        </span>
                      </td>

                      <td>
                        <span className="index-value">
                          #{fragmentIndex}
                        </span>
                      </td>

                      <td>
                        {size != null
                          ? `${formatNumber(size)} B`
                          : "—"}
                      </td>

                      <td>
                        <div className="entropy">
                          <Activity size={13} />

                          {typeof fragmentEntropy ===
                          "number"
                            ? fragmentEntropy.toFixed(
                                3
                              )
                            : "—"}
                        </div>
                      </td>

                      <td>
                        <div className="confidence-cell">

                          <div className="confidence-track">
                            <span
                              style={{
                                width: `${Math.min(
                                  100,
                                  Math.max(
                                    0,
                                    Number(
                                      confidence <= 1
                                        ? confidence * 100
                                        : confidence
                                    ) || 0
                                  )
                                )}%`,
                              }}
                            />
                          </div>

                          <strong>
                            {formatConfidence(
                              confidence
                            )}
                          </strong>

                        </div>
                      </td>

                      <td>
                        <ChevronRight
                          size={16}
                          className="row-arrow"
                        />
                      </td>

                    </tr>
                  );
                }
              )}
            </tbody>

          </table>

          {filteredFragments.length === 0 && (
            <div className="no-fragments">

              <Database size={30} />

              <strong>
                {search
                  ? "No matching fragments"
                  : "No fragments available"}
              </strong>

              <span>
                {search
                  ? "Try a different search term."
                  : "Run a forensic scan to populate fragment intelligence."}
              </span>

            </div>
          )}

        </div>
      </section>

      {/* ================================================= */}
      {/* RELATIONSHIPS */}
      {/* ================================================= */}

      <section className="relationships-section">

        <div className="section-heading">

          <div>
            <p className="eyebrow">
              AI RELATIONSHIP ENGINE
            </p>

            <h2>Fragment Relationships</h2>

            <p>
              Machine-learning signals connecting
              fragments that may belong to the same
              reconstructed evidence chain.
            </p>
          </div>

          <div className="relationship-badge">
            <Network size={15} />

            {formatNumber(
              strongRelationships
            )}{" "}
            strong links
          </div>

        </div>

        {relationships.length > 0 ? (

          <div className="relationship-grid">

            {relationships
              .slice(0, 12)
              .map(
                (relationship, index) => {

                  const from =
                    relationship.from_fragment ||
                    relationship.source_fragment ||
                    relationship.fragment_a ||
                    relationship.from ||
                    `FRAG_${String(
                      index + 1
                    ).padStart(6, "0")}`;

                  const to =
                    relationship.to_fragment ||
                    relationship.target_fragment ||
                    relationship.fragment_b ||
                    relationship.to ||
                    `FRAG_${String(
                      index + 2
                    ).padStart(6, "0")}`;

                  const probability =
                    relationship.probability ??
                    relationship.confidence ??
                    relationship.score ??
                    0;

                  return (
                    <div
                      className="relationship-card"
                      key={
                        relationship.relationship_id ||
                        index
                      }
                    >

                      <div className="relationship-nodes">

                        <span>{from}</span>

                        <div className="relationship-line">

                          <span />

                          <strong>
                            {formatConfidence(
                              probability
                            )}
                          </strong>

                          <span />

                        </div>

                        <span>{to}</span>

                      </div>

                      <div className="relationship-meta">
                        <Zap size={13} />
                        AI relationship signal
                      </div>

                    </div>
                  );
                }
              )}

          </div>

        ) : (

          <div className="empty-relationships">

            <Network size={28} />

            <strong>
              No relationship data available
            </strong>

            <span>
              Relationship analysis will appear
              after a live forensic scan.
            </span>

          </div>

        )}

      </section>

      {/* ================================================= */}
      {/* INSPECTOR */}
      {/* ================================================= */}

      {selectedFragment && (

        <aside className="fragment-inspector">

          <div className="inspector-header">

            <div>
              <p className="eyebrow">
                FRAGMENT INSPECTOR
              </p>

              <h3>
                {selectedFragment.fragment_id ||
                  selectedFragment.id ||
                  "Fragment"}
              </h3>
            </div>

            <button
              type="button"
              onClick={() =>
                setSelectedFragment(null)
              }
            >
              ×
            </button>

          </div>

          <div className="inspector-grid">

            <div>
              <span>FILE TYPE</span>

              <strong>
                {String(
                  selectedFragment.file_type ||
                    selectedFragment.type ||
                    fileType
                ).toUpperCase()}
              </strong>
            </div>

            <div>
              <span>INDEX</span>

              <strong>
                {selectedFragment.fragment_index ??
                  selectedFragment.index ??
                  "—"}
              </strong>
            </div>

            <div>
              <span>SIZE</span>

              <strong>
                {selectedFragment.size ??
                  selectedFragment.fragment_size ??
                  "—"}
                {" B"}
              </strong>
            </div>

            <div>
              <span>ENTROPY</span>

              <strong>
                {typeof selectedFragment.entropy ===
                "number"
                  ? selectedFragment.entropy.toFixed(
                      3
                    )
                  : "—"}
              </strong>
            </div>

          </div>

          <div className="inspector-note">

            <ShieldCheck size={17} />

            <div>
              <strong>
                Evidence handling
              </strong>

              <p>
                Fragment data is displayed from
                the current live recovery session.
                AI-derived values should be treated
                as analytical signals rather than
                standalone forensic proof.
              </p>
            </div>

          </div>

        </aside>
      )}

    </div>
  );
}

export default Fragments;