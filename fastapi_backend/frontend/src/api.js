const API_URL = "http://localhost:8000";

export async function apiFetch(endpoint, options = {}) {
  let accessToken = localStorage.getItem("access_token");

  const makeRequest = (token) => {
    const headers = {
      ...(options.headers || {}),
    };

    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }

    return fetch(`${API_URL}${endpoint}`, {
      ...options,
      headers,
    });
  };

  let response = await makeRequest(accessToken);

  if (response.status === 401) {
    const refreshToken =
      localStorage.getItem("refresh_token");

    if (!refreshToken) {
      logout();
      return response;
    }

    try {
      const refreshResponse = await fetch(
        `${API_URL}/auth/refresh`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            refresh_token: refreshToken,
          }),
        }
      );

      if (!refreshResponse.ok) {
        logout();
        return refreshResponse;
      }

      const tokenData =
        await refreshResponse.json();

      localStorage.setItem(
        "access_token",
        tokenData.access_token
      );

      if (tokenData.refresh_token) {
        localStorage.setItem(
          "refresh_token",
          tokenData.refresh_token
        );
      }

      response = await makeRequest(
        tokenData.access_token
      );
    } catch (error) {
      logout();
    }
  }

  return response;
}

export function logout() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  localStorage.removeItem("user");

  window.location.href = "/";
}

export function getCurrentUser() {
  try {
    const user = localStorage.getItem("user");

    return user ? JSON.parse(user) : null;
  } catch {
    return null;
  }
}