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
  if (method === "GET" && url === "/api/lecturers") {
    return Promise.resolve([
      { id: 1, name: "Bukasa", email: "bukasa@example.com" },
      { id: 2, name: "Kudzai", email: "kudzai@example.com" }
    ]);
  }

  if (method === "GET" && url === "/api/courses") {
    return Promise.resolve([
      { id: 1, code: "IT101", name: "Introduction to IT" },
      { id: 2, code: "DB201", name: "Database Systems" }
    ]);
  }

  if (method === "GET" && url === "/api/rooms") {
    return Promise.resolve([
      { id: 1, name: "Room A", capacity: 40 },
      { id: 2, name: "Computer Lab 1", capacity: 30 }
    ]);
  }

  if (method === "GET" && url === "/api/student-groups") {
    return Promise.resolve([
      { id: 1, name: "Group 1", year_level: 1, size: 35 },
      { id: 2, name: "Group 2", year_level: 2, size: 28 }
    ]);
  }

  if (method === "GET" && url === "/api/time-slots") {
    return Promise.resolve([
      {
        id: 1,
        day_of_week: "Monday",
        start_time: "08:15",
        end_time: "09:15",
        is_break: false
      },
      {
        id: 2,
        day_of_week: "Tuesday",
        start_time: "09:15",
        end_time: "10:15",
        is_break: false
      }
    ]);
  }

  return Promise.resolve([]);
}

