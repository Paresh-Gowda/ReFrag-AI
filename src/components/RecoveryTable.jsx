
const defaultArtifacts = [
  {
    id: "art-1",
    name: "IMG_2048.jpg",
    type: "JPEG",
    integrity: "92%",
    confidence: "95%",
    status: "Reconstructed",
    statusType: "recovered",
  },
  {
    id: "art-2",
    name: "financial_report.pdf",
    type: "PDF",
    integrity: "78%",
    confidence: "88%",
    status: "Partial",
    statusType: "partial",
  },
  {
    id: "art-3",
    name: "archive_07.zip",
    type: "ZIP",
    integrity: "96%",
    confidence: "97%",
    status: "Reconstructed",
    statusType: "recovered",
  },
  {
    id: "art-4",
    name: "evidence_vault.db",
    type: "SQLITE",
    integrity: "85%",
    confidence: "90%",
    status: "Partial",
    statusType: "partial",
  },
];

function RecoveryTable({ artifacts = defaultArtifacts }) {
  return (
    <div className="evidence-table">
      <div className="table-header">
        <span>Artifact</span>
        <span>Type</span>
        <span>Integrity</span>
        <span>Confidence</span>
        <span>Status</span>
      </div>

      {artifacts.map((item) => (
        <div key={item.id || item.name} className="table-row">
          <span className="artifact-name">{item.name}</span>
          <span>{item.type}</span>
          <span>{item.integrity}</span>
          <span>{item.confidence}</span>
          <span className={`status ${item.statusType || (item.status === "Reconstructed" ? "recovered" : "partial")}`}>
            {item.status}
          </span>
        </div>
      ))}
    </div>
  );
}

export default RecoveryTable;
