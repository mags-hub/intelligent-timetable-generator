// Login, logout and role-based redirects.  (Ticket 3)
// The server (Ticket 5) is the real gatekeeper; this only gives a clean user experience.
import { api } from "./api.js";

export const HOME = {
  admin: "/admin/dashboard.html",
  lecturer: "/view/timetable.html",
  student: "/view/timetable.html",
};

export function handleLoginForm(form) {
  const error = document.getElementById("login-error");
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    error.hidden = true;
    const button = form.querySelector("button[type=submit]");
    button.disabled = true;
    try {
      const user = await api.post("/api/auth/login", {
        username: form.username.value.trim(),
        password: form.password.value,
      });
      window.location.href = HOME[user.role] || "/login.html";
    } catch (err) {
      error.textContent = err.status === 401 ? "Wrong username or password" : err.message;
      error.hidden = false;
      button.disabled = false;
    }
  });
}

// Used by index.html: go to the right home page, or to the sign-in page (api.js does that on 401).
export async function redirectByRole() {
  const user = await api.get("/api/auth/me");
  window.location.href = HOME[user.role] || "/login.html";
}

// Call at the top of every protected page. Returns the signed-in user.
export async function requireRole(...roles) {
  const user = await api.get("/api/auth/me");
  if (!roles.includes(user.role)) {
    window.location.href = HOME[user.role] || "/login.html";
    return new Promise(() => {});
  }
  return user;
}

export function handleLogout(button) {
  button.addEventListener("click", async () => {
    try { await api.post("/api/auth/logout"); } finally { window.location.href = "/login.html"; }
  });
}
// Builds the greeting, e.g. "Hi Lecturer Bukasa". Just "Hi Admin" if the username equals the role.
export function greeting(user) {
  const cap = (s) => s.charAt(0).toUpperCase() + s.slice(1);
  const role = cap(user.role);
  return user.username.toLowerCase() === user.role
    ? `Hi ${role}`
    : `Hi ${role} ${cap(user.username)}`;
}
