// The timetable grid (shared by the admin preview and the lecturer/student page).  (Ticket 4)
import { api } from "./api.js";

export const DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];
export const HOURS = ["08:15", "09:15", "10:15", "11:15", "12:15", "13:15", "14:15", "15:15"]; // 12:15 = lunch
const LUNCH = "12:15";
const COLOURS = ["#dbe7f3", "#e2efda", "#fff2cc", "#fce4d6", "#ede2f6", "#e2f0f0", "#f6e3ec", "#e8ecd2"];

// The same course always gets the same colour.
export function colourFor(code) {
  let sum = 0;
  for (const ch of code || "") sum = (sum * 31 + ch.charCodeAt(0)) % 997;
  return COLOURS[sum % COLOURS.length];
}

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

// A combined class comes back once per group: show it once and list its groups.
export function mergeEntries(entries) {
  const byId = new Map();
  for (const e of entries) {
    if (byId.has(e.entry_id)) byId.get(e.entry_id).group_names.push(e.group_name);
    else byId.set(e.entry_id, { ...e, group_names: [e.group_name] });
  }
  return [...byId.values()];
}

// Rows = hours, columns = days. options: { show: {lecturer, group}, onSelect(entry) }
export function renderWeekGrid(entries, container, options = {}) {
  const show = options.show || { lecturer: true, group: false };
  const merged = mergeEntries(entries);
  const hours = [...new Set([...HOURS, ...merged.map((e) => e.start_time)])].sort();

  const table = el("table", "week");
  const caption = el("caption", "muted", "Weekly timetable");
  caption.style.textAlign = "left";
  table.appendChild(caption);
  const head = el("tr");
  head.appendChild(el("th", "time", "Time"));
  for (const day of DAYS) head.appendChild(el("th", "", day));
  table.appendChild(head);

  for (const hour of hours) {
    const tr = el("tr");
    tr.appendChild(el("th", "time", hour));
    DAYS.forEach((day, index) => {
      const td = el("td");
      if (hour === LUNCH) {
        td.className = "lunch";
        if (index === 2) td.textContent = "Lunch";
      }
      for (const entry of merged.filter((e) => e.day_of_week === index + 1 && e.start_time === hour)) {
        const cell = options.onSelect ? el("button", "cell") : el("div", "cell");
        if (options.onSelect) {
          cell.type = "button";
          cell.title = "Click to move this class";
          cell.addEventListener("click", () => options.onSelect(entry));
        }
        cell.style.background = colourFor(entry.course_code);
        cell.appendChild(el("strong", "", entry.course_code));
        cell.appendChild(el("small", "", entry.room));
        if (show.lecturer && entry.lecturer) cell.appendChild(el("small", "", entry.lecturer));
        if (show.group) cell.appendChild(el("small", "", entry.group_names.join(", ")));
        td.appendChild(cell);
      }
      tr.appendChild(td);
    });
    table.appendChild(tr);
  }
  const wrap = el("div", "scroll-x");
  wrap.appendChild(table);
  container.replaceChildren(wrap);
}

// One day as a list of cards: the phone-friendly view.
export function renderDayList(entries, day, container, show = { lecturer: true, group: false }) {
  const merged = mergeEntries(entries).filter((e) => e.day_of_week === day)
    .sort((a, b) => a.start_time.localeCompare(b.start_time));
  const title = el("h2", "", DAYS[day - 1]);
  if (merged.length === 0) {
    container.replaceChildren(title, el("p", "muted", "No classes on this day."));
    return;
  }
  const list = el("ul", "daylist");
  for (const entry of merged) {
    const li = el("li");
    li.style.background = colourFor(entry.course_code);
    li.appendChild(el("span", "room", entry.room));
    li.appendChild(el("div", "time", `${entry.start_time}-${entry.end_time}`));
    li.appendChild(el("strong", "", `${entry.course_code}  ${entry.course_name}`));
    const extra = [];
    if (show.lecturer && entry.lecturer) extra.push(entry.lecturer);
    if (show.group) extra.push(entry.group_names.join(", "));
    if (extra.length) li.appendChild(el("div", "muted", extra.join("  |  ")));
    list.appendChild(li);
  }
  container.replaceChildren(title, list);
}

export async function initTimetableView(user) {
  const area = document.getElementById("timetable-area");
  const empty = document.getElementById("empty-state");
  const toggle = document.querySelectorAll("#view-toggle button");
  const sub = document.getElementById("subtitle");

  const data = await api.get("/api/timetables/published/mine");
  if (!data.published || data.entries.length === 0) {
    empty.hidden = false;
    document.getElementById("view-toggle").hidden = true;
    return;
  }
  if (sub) sub.textContent = data.name || "";

  // a student sees the lecturer, a lecturer sees the group
  const show = { lecturer: user.role === "student", group: user.role === "lecturer" };
  const jsDay = new Date().getDay();                 // 0 = Sunday
  let day = jsDay >= 1 && jsDay <= 5 ? jsDay : 1;
  let view = window.matchMedia("(max-width: 700px)").matches ? "day" : "week";

  function draw() {
    toggle.forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.view === view)));
    if (view === "week") {
      renderWeekGrid(data.entries, area, { show });
    } else {
      const tabs = el("div", "daytabs");
      DAYS.forEach((name, i) => {
        const b = el("button", "", name.slice(0, 3));
        b.type = "button";
        b.setAttribute("aria-pressed", String(i + 1 === day));
        b.addEventListener("click", () => { day = i + 1; draw(); });
        tabs.appendChild(b);
      });
      const list = el("div");
      renderDayList(data.entries, day, list, show);
      area.replaceChildren(tabs, list);
    }
  }
  toggle.forEach((b) => b.addEventListener("click", () => { view = b.dataset.view; draw(); }));
  draw();
}
