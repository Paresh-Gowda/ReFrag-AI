const API_BASE = "http://localhost:8000/api";

async function request(endpoint, options = {}) {
  const response = await fetch(`${API_BASE}${endpoint}`, options);

  let data;

  try {
    data = await response.json();
  } catch {
    throw new Error("Backend returned an invalid response.");
  }

  if (!response.ok) {
    throw new Error(
      data?.detail ||
      data?.message ||
      "Request failed."
    );
  }

  return data;
}


/* =========================================================
   DASHBOARD
========================================================= */

export async function getDashboard() {
  return request("/dashboard");
}


/* =========================================================
   EVIDENCE
========================================================= */

export async function getEvidence() {
  return request("/evidence");
}

export async function getTopEvidence() {
  return request("/evidence/top");
}


/* =========================================================
   FRAGMENTS
========================================================= */

export async function getFragments() {
  return request("/fragments");
}


/* =========================================================
   ANALYTICS
========================================================= */

export async function getAnalytics() {
  return request("/analytics");
}


/* =========================================================
   HEALTH
========================================================= */

export async function getHealth() {
  return request("/health");
}


/* =========================================================
   SYSTEM
========================================================= */

export async function getSystem() {
  return request("/system");
}


/* =========================================================
   LIVE VISUAL RESULT
========================================================= */

export async function getVisualRecoveryResult() {
  return request("/image-recovery/result");
}


/* =========================================================
   LIVE SESSION
========================================================= */

export async function getLiveSession() {
  return request("/dashboard");
}


/* =========================================================
   FORENSIC SCAN
========================================================= */

export async function scanFile(file) {
  const formData = new FormData();

  formData.append("file", file);

  return request("/scan", {
    method: "POST",
    body: formData,
  });
}


/* =========================================================
   VISUAL IMAGE RECOVERY
========================================================= */

export async function recoverImage(file) {
  const formData = new FormData();

  formData.append("file", file);

  return request("/image-recovery", {
    method: "POST",
    body: formData,
  });
}


/* =========================================================
   CLEAR LIVE SESSION
========================================================= */

export async function clearLiveSession() {
  return request("/scan", {
    method: "DELETE",
  });
}