// Drives admin/generate.html: generate, preview, adjust, publish.  (Ticket 3, uses Ticket 6)
import { api } from "./api.js";
import { renderWeekGrid, DAYS } from "./timetable.js";

function el(tag, text, cls) { const n = document.createElement(tag); if (text !== undefined) n.textContent = text; if (cls) n.className = cls; return n; }

export async function initGeneratePage() {
  const form = document.getElementById("generate-form");
  const status = document.getElementById("status");
  const preview = document.getElementById("preview");
  const publishButton = document.getElementById("publish");
  const existing = document.getElementById("existing");
  const moveDialog = document.getElementById("move-dialog");
  const moveForm = document.getElementById("move-form");

  let current = null;           // the timetable being previewed: { id, status, name, entries }
  let rooms = [];
  let slots = [];

  function say(text, kind = "info") { status.textContent = text; status.className = `msg ${kind}`; }

  // ---------- the list of existing timetables ----------
  async function loadList() {
    const list = await api.get("/api/timetables");
    existing.replaceChildren();
    if (list.length === 0) { existing.appendChild(el("p", "No timetables yet.", "muted")); return; }
    const table = el("table");
    const head = el("tr");
    for (const h of ["Name", "Semester", "Year", "Status", ""]) head.appendChild(el("th", h));
    table.appendChild(head);
    for (const t of list) {
      const tr = el("tr");
      tr.append(el("td", t.name), el("td", String(t.semester)), el("td", String(t.academic_year)));
      const st = el("td"); st.appendChild(el("span", t.status, `badge ${t.status}`)); tr.appendChild(st);
      const open = el("td"); const b = el("button", "Open", "secondary"); b.type = "button";
      b.addEventListener("click", () => loadTimetable(t.id)); open.appendChild(b); tr.appendChild(open);
      table.appendChild(tr);
    }
    const wrap = el("div", undefined, "scroll-x"); wrap.appendChild(table);
    existing.appendChild(wrap);
  }

  // ---------- the preview ----------
  async function loadTimetable(id, keepGroup) {
    const data = await api.get(`/api/timetables/${id}`);
    current = data;
    const names = [...new Set(data.entries.map((e) => e.group_name))].sort();
    preview.replaceChildren();
    const title = el("h2", `${data.name} `);
    title.appendChild(el("span", data.status, `badge ${data.status}`));
    preview.appendChild(title);

    const label = el("label", "Show the timetable of"); label.htmlFor = "group-select";
    const select = el("select"); select.id = "group-select";
    for (const n of ["All groups", ...names]) { const o = el("option", n); o.value = n; select.appendChild(o); }
    select.value = keepGroup && ["All groups", ...names].includes(keepGroup) ? keepGroup : (names[0] || "All groups");
    const gridBox = el("div");
    const hint = el("p", "Click a class to move it to another room or time. A moved class is locked, so regenerating will not move it again.", "muted");
    function draw() {
      const chosen = select.value;
      const entries = chosen === "All groups" ? data.entries : data.entries.filter((e) => e.group_name === chosen);
      renderWeekGrid(entries, gridBox, { show: { lecturer: true, group: chosen === "All groups" }, onSelect: openMove });
    }
    select.addEventListener("change", draw);
    preview.append(label, select, hint, gridBox);
    draw();
    publishButton.hidden = data.status !== "draft";
    publishButton.disabled = false;
    preview.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  // ---------- moving one class ----------
  function openMove(entry) {
    moveForm.replaceChildren();
    moveForm.appendChild(el("h2", `Move ${entry.course_code}`));
    moveForm.appendChild(el("p", `Now: ${DAYS[entry.day_of_week - 1]} ${entry.start_time}-${entry.end_time}, room ${entry.room}`, "muted"));

    const lr = el("label", "Room"); lr.htmlFor = "m-room";
    const room = el("select"); room.id = "m-room"; room.name = "room_id";
    for (const r of rooms) { const o = el("option", `${r.name} (${r.capacity} seats, ${r.room_type})`); o.value = r.id; if (r.name === entry.room) o.selected = true; room.appendChild(o); }
    const ls = el("label", "Day and time"); ls.htmlFor = "m-slot";
    const slot = el("select"); slot.id = "m-slot"; slot.name = "time_slot_id";
    for (const s of slots.filter((x) => !x.is_break)) {
      const o = el("option", `${DAYS[s.day_of_week - 1]} ${s.start_time}-${s.end_time}`); o.value = s.id;
      if (s.day_of_week === entry.day_of_week && s.start_time === entry.start_time) o.selected = true;
      slot.appendChild(o);
    }
    const error = el("p", ""); error.setAttribute("role", "alert"); error.hidden = true;
    const actions = el("div", undefined, "actions");
    const save = el("button", "Move"); save.type = "submit";
    const cancel = el("button", "Cancel", "secondary"); cancel.type = "button"; cancel.addEventListener("click", () => moveDialog.close());
    actions.append(save, cancel);
    moveForm.append(lr, room, ls, slot, error, actions);

    moveForm.onsubmit = async (event) => {
      event.preventDefault();
      error.hidden = true; save.disabled = true;
      try {
        await api.put(`/api/timetables/${current.id}/entries/${entry.entry_id}`, { room_id: Number(room.value), time_slot_id: Number(slot.value) });
        moveDialog.close();
        say(`Moved ${entry.course_code}.`, "ok");
        const group = document.getElementById("group-select")?.value;
        await loadTimetable(current.id, group);
      } catch (err) { error.textContent = err.message; error.hidden = false; }    // the clash reason from the server
      finally { save.disabled = false; }
    };
    moveDialog.showModal();
  }

  // ---------- generate ----------
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const button = form.querySelector("button[type=submit]");
    button.disabled = true;
    say("Generating... this can take up to 20 seconds. Please wait.", "info");
    try {
      const result = await api.post("/api/timetables/generate", {
        semester: Number(form.semester.value),
        academic_year: Number(form.year.value),
      });
      const score = typeof result.score === "number" ? ` Score: ${result.score.toFixed(2)} (closer to 0 is better).` : "";
      say(`Draft timetable created.${score} Review it below, then publish it.`, "ok");
      await loadList();
      await loadTimetable(result.timetable_id);
    } catch (err) {
      say(err.message, "error");                       // for example "No room is large enough for ..."
    } finally { button.disabled = false; }
  });

  // ---------- publish ----------
  publishButton.addEventListener("click", async () => {
    if (!current) return;
    if (!window.confirm("Publish this timetable? Lecturers and students will be able to see it, and the previously published one will be archived.")) return;
    publishButton.disabled = true;
    try {
      await api.post(`/api/timetables/${current.id}/publish`);
      say("Published. Lecturers and students can now see this timetable.", "ok");
      await loadList();
      await loadTimetable(current.id, document.getElementById("group-select")?.value);
    } catch (err) { say(err.message, "error"); publishButton.disabled = false; }
  });

  [rooms, slots] = await Promise.all([api.get("/api/rooms"), api.get("/api/time-slots")]);
  await loadList();
}
