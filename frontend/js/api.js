// All backend calls go through here. Pages never call fetch() directly.

// While the backend is unfinished, set USE_MOCK = true and return fake data from `mock()`.
export const USE_MOCK = false;

async function request(method, url, body) {
  if (USE_MOCK) return mock(method, url, body);

  const res = await fetch(url, {
    method,
    headers: body ? { "Content-Type": "application/json" } : undefined,
    body: body ? JSON.stringify(body) : undefined,
    credentials: "same-origin",
  });

  // Not signed in: send the user to the sign-in page. The login request itself is the one
  // exception, because a 401 there only means "wrong password" and must be shown on the form.
  if (res.status === 401 && url !== "/api/auth/login") {
    window.location.href = "/login.html";
    return new Promise(() => {});               // stop the caller
  }
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    // Callers show err.message to the user (e.g. the clash reason from a 409).
    const err = new Error(data.error || data.message || `Request failed (${res.status})`);
    err.status = res.status;
    throw err;
  }
  return data;
}

export const api = {
  get: (url) => request("GET", url),
  post: (url, body) => request("POST", url, body),
  put: (url, body) => request("PUT", url, body),
  del: (url) => request("DELETE", url),
};

function mock() {
  return Promise.resolve([]);
}
