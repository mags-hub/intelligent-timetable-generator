// Drives admin/dashboard.html.  (Ticket 3)
import { api } from "./api.js";

const KINDS = [
  ["lecturers", "Lecturers"],
  ["courses", "Courses"],
  ["rooms", "Rooms"],
  ["student-groups", "Student groups"],
  ["time-slots", "Time slots"],
];

export async function initDashboard() {
  const cards = document.getElementById("cards");
  const lists = await Promise.all(KINDS.map(([type]) => api.get(`/api/${type}`)));
  KINDS.forEach(([type, title], i) => {
    const card = document.createElement("div");
    card.className = "card";
    card.innerHTML = '<div class="muted"></div><div class="count"></div><a>Manage</a>';
    card.children[0].textContent = title;
    card.children[1].textContent = lists[i].length;
    card.children[2].href = `/admin/manage.html?type=${type}`;
    card.children[2].textContent = "Manage ->";
    cards.appendChild(card);
  });

  const panel = document.getElementById("latest");
  const timetables = await api.get("/api/timetables");          // newest first
  const latest = timetables[0];
  const published = timetables.find((t) => t.status === "published");
  panel.replaceChildren();
  const add = (tag, text, cls) => { const n = document.createElement(tag); if (cls) n.className = cls; n.textContent = text; panel.appendChild(n); return n; };
  if (!latest) {
    add("h2", "No timetable yet");
    add("p", "Press Generate to build the first one.");
  } else {
    add("h2", "Latest timetable");
    const p = add("p", `${latest.name} `);
    add("span", latest.status, `badge ${latest.status}`).style.marginLeft = "0.3rem";
    if (latest.status === "draft") add("p", "A draft is not visible to lecturers and students until you publish it.", "muted");
    if (published) add("p", `Published for students and lecturers: ${published.name}`, "muted");
    p.appendChild(document.createTextNode(""));
  }
  const link = document.createElement("a");
  link.href = "/admin/generate.html";
  link.textContent = latest && latest.status === "draft" ? "Review the draft and publish it ->" : "Generate a new timetable ->";
  link.style.fontWeight = "600";
  panel.appendChild(link);
}
