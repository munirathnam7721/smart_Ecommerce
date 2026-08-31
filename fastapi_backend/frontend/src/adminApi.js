const API_BASE_URL = "http://localhost:8000";

function getToken() {
  return (
    localStorage.getItem("access_token") ||
    localStorage.getItem("token")
  );
}

async function request(url, options = {}) {
  const token = getToken();

  const response = await fetch(
    `${API_BASE_URL}${url}`,
    {
      ...options,
      headers: {
        ...(options.headers || {}),
        ...(token
          ? {
              Authorization: `Bearer ${token}`,
            }
          : {}),
      },
    }
  );

  if (!response.ok) {
    let message = "Request failed";

    try {
      const data = await response.json();
      message = data.detail || message;
    } catch {
      // Ignore JSON parsing error
    }

    throw new Error(message);
  }

  return response;
}


// ============================================================
// ADMIN DASHBOARD
// ============================================================

export async function getAdminDashboard(
  lowStockThreshold = 5
) {
  const response = await request(
    `/admin/analytics/dashboard?low_stock_threshold=${lowStockThreshold}`
  );

  return response.json();
}


// ============================================================
// REPORT DOWNLOAD
// ============================================================

export async function downloadReport(
  reportType,
  format
) {
  const response = await request(
    `/admin/reports/${reportType}/${format}`
  );

  const blob = await response.blob();

  const contentDisposition =
    response.headers.get("Content-Disposition");

  let filename = `${reportType}.${format}`;

  if (contentDisposition) {
    const match =
      contentDisposition.match(
        /filename="?([^"]+)"?/i
      );

    if (match) {
      filename = match[1];
    }
  }

  const url = window.URL.createObjectURL(blob);

  const link = document.createElement("a");

  link.href = url;
  link.download = filename;

  document.body.appendChild(link);

  link.click();

  link.remove();

  window.URL.revokeObjectURL(url);
}