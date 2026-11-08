// The navigation bar shared by every admin page.
import { handleLogout } from "./auth.js";

const LINKS = [
  ["Dashboard", "/admin/dashboard.html"],
  ["Lecturers", "/admin/manage.html?type=lecturers"],
  ["Courses", "/admin/manage.html?type=courses"],
  ["Rooms", "/admin/manage.html?type=rooms"],
  ["Student groups", "/admin/manage.html?type=student-groups"],
  ["Time slots", "/admin/manage.html?type=time-slots"],
  ["Generate timetable", "/admin/generate.html"],
];

// `active` is the link text to highlight, for example "Rooms".
export function renderAdminNav(active) {
  const header = document.getElementById("nav");
  header.className = "bar";
  header.innerHTML = '<div class="inner"><nav class="top" aria-label="Admin sections"></nav>' +
    '<button id="logout" type="button">Sign out</button></div>';
  const nav = header.querySelector("nav");
  for (const [text, href] of LINKS) {
    const a = document.createElement("a");
    a.textContent = text;
    a.href = href;
    if (text === active) a.setAttribute("aria-current", "page");
    nav.appendChild(a);
  }
  handleLogout(document.getElementById("logout"));
}
