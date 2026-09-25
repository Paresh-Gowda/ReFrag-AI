/**
 * API service for Forensic Data Ingestion
 */

const API_BASE = "/api/forensics";

export async function uploadForensicDataset(files, relativePaths = [], caseName = "") {
  const formData = new FormData();

  files.forEach((file, index) => {
    formData.append("files", file);
    const relPath = relativePaths[index] || file.webkitRelativePath || file.name;
    formData.append("relative_paths", relPath);
  });

  if (caseName) {
    formData.append("case_name", caseName);
  }

  try {
    const response = await fetch(`${API_BASE}/upload`, {
      method: "POST",
      body: formData,
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || `Upload failed with status ${response.status}`);
    }

    return data;
  } catch (error) {
    if (error.message && error.message.includes("Failed to fetch")) {
      throw new Error("Unable to connect to backend server. Please verify backend service is active.");
    }
    throw error;
  }
}

export async function getCaseDetails(caseId) {
  const response = await fetch(`${API_BASE}/cases/${caseId}`);
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || "Failed to fetch case details.");
  }
  return data;
}

export async function getArtifactDetails(artifactId) {
  const response = await fetch(`${API_BASE}/artifacts/${artifactId}`);
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || "Failed to fetch artifact details.");
  }
  return data;
}
