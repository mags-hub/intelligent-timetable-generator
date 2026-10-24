// All backend calls go through here. Pages never call fetch() directly.

// While Ticket 6 is unfinished, set USE_MOCK = true and return fake data from `mock()`.
export const USE_MOCK = false;

async function request(method, url, body) {
  if (USE_MOCK) return mock(method, url, body);

  const res = await fetch(url, {
    method,
    headers: body ? { "Content-Type": "application/json" } : undefined,
    body: body ? JSON.stringify(body) : undefined,
    credentials: "same-origin",
  });

  if (res.status === 401) {
    window.location.href = "/login.html";       // not signed in
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

function mock(method, url, body) {
  // TODO (Ticket 3): return realistic sample data, e.g. for GET /api/lecturers:
  //   [{ id: 1, name: "Bukasa" }, { id: 2, name: "Kudzai" }]
  return Promise.resolve([]);
}
