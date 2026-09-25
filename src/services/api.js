const API_BASE = "http://localhost:8000/api";

async function request(endpoint) {
  const response = await fetch(`${API_BASE}${endpoint}`);

  if (!response.ok) {
    throw new Error(
      `API request failed: ${response.status}`
    );
  }

  return response.json();
}

export async function getDashboard() {
  return request("/dashboard");
}

export async function getEvidence() {
  return request("/evidence");
}

export async function getTopEvidence() {
  return request("/evidence/top");
}

export async function getFragments() {
  return request("/fragments");
}

export async function getAnalytics() {
  return request("/analytics");
}

export async function getHealth() {
  return request("/health");
}