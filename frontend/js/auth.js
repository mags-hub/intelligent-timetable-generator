// Login, logout and role-based redirects.  TODO (Ticket 3)
import { api } from "./api.js";

const HOME = { admin: "/admin/dashboard.html", lecturer: "/view/timetable.html", student: "/view/timetable.html" };

export async function handleLoginForm(form) {
  // TODO (Ticket 3): on submit -> api.post("/api/auth/login", {username, password}),
  //   then go to HOME[user.role]. On a 401, show "Wrong username or password" in #login-error.
}

export async function redirectByRole() {
  // TODO (Ticket 3): api.get("/api/auth/me") -> HOME[role]; if not signed in, go to /login.html.
}

export async function requireRole(...roles) {
  // TODO (Ticket 3): call /api/auth/me; if the role is not in `roles`, redirect to that user's HOME.
  //   The server is the real gatekeeper (Ticket 5); this only gives a clean user experience.
}

export function handleLogout(button) {
  // TODO (Ticket 3): on click -> api.post("/api/auth/logout") then go to /login.html.
}
