// Drives admin/manage.html.  (Ticket 3)
import { api } from "./api.js";

const DAY_NAMES = { 1: "Mon", 2: "Tue", 3: "Wed", 4: "Thu", 5: "Fri" };
const ROOM_TYPES = ["lecture", "lab", "auditorium"];
const YEARS = [1, 2, 3, 4];

// One config per data type: which fields to show and edit. Keeps one page for all five.
//   kind: text | number | select | checkbox      required: the server needs a value
//   options: a list of [value, label] pairs, or the name of a type to load from the API
export const TYPES = {
  "lecturers": { title: "Lecturers", singular: "lecturer", fields: [
    { name: "name", label: "Name", kind: "text", required: true },
    { name: "email", label: "Email (optional)", kind: "text" },
    { name: "is_active", label: "Active", kind: "checkbox", default: 1 },
  ] },
  "courses": { title: "Courses", singular: "course", groups: true, fields: [
    { name: "code", label: "Course code", kind: "text", required: true },
    { name: "name", label: "Course name", kind: "text", required: true },
    { name: "year_level", label: "Year level", kind: "select", required: true, options: YEARS.map((y) => [y, `Year ${y}`]) },
    { name: "lecturer_id", label: "Lecturer", kind: "select", required: true, options: "lecturers" },
    { name: "weekly_hours", label: "Hours per week", kind: "number", required: true, default: 4 },
    { name: "block_hours", label: "Hours kept together (block)", kind: "number", required: true, default: 1 },
    { name: "preferred_room_type", label: "Preferred room type", kind: "select", options: ROOM_TYPES.map((t) => [t, t]), blank: "No preference" },
    { name: "is_elective", label: "Elective", kind: "checkbox", default: 0 },
  ] },
  "rooms": { title: "Rooms", singular: "room", fields: [
    { name: "name", label: "Room name", kind: "text", required: true },
    { name: "room_type", label: "Type", kind: "select", required: true, options: ROOM_TYPES.map((t) => [t, t]) },
    { name: "capacity", label: "Capacity (seats)", kind: "number", required: true },
    { name: "campus", label: "Campus", kind: "text" },
  ] },
  "student-groups": { title: "Student groups", singular: "student group", fields: [
    { name: "name", label: "Group name", kind: "text", required: true },
    { name: "year_level", label: "Year level", kind: "select", required: true, options: YEARS.map((y) => [y, `Year ${y}`]) },
    { name: "size", label: "Number of students", kind: "number", required: true },
    { name: "parent_group_id", label: "Parent group (for elective streams)", kind: "select", options: "student-groups", blank: "None" },
  ] },
  "time-slots": { title: "Time slots", singular: "time slot", fields: [
    { name: "day_of_week", label: "Day", kind: "select", required: true, options: Object.entries(DAY_NAMES).map(([v, l]) => [Number(v), l]) },
    { name: "start_time", label: "Start time (HH:MM)", kind: "text", required: true },
    { name: "end_time", label: "End time (HH:MM)", kind: "text", required: true },
    { name: "is_break", label: "Break (no classes)", kind: "checkbox", default: 0 },
  ] },
};

function el(tag, text, cls) { const n = document.createElement(tag); if (text !== undefined) n.textContent = text; if (cls) n.className = cls; return n; }

export async function initManagePage() {
  const type = new URLSearchParams(window.location.search).get("type");
  const config = TYPES[type];
  const status = document.getElementById("status");
  const area = document.getElementById("table-area");
  const dialog = document.getElementById("edit-dialog");
  const form = document.getElementById("edit-form");
  const addButton = document.getElementById("add-button");

  function say(text, kind = "info") { status.textContent = text; status.className = `msg ${kind}`; }

  if (!config) {
    document.getElementById("page-title").textContent = "Unknown section";
    addButton.hidden = true;
    area.replaceChildren(el("p", "Choose a section from the menu above."));
    return;
  }
  document.getElementById("page-title").textContent = config.title;
  addButton.textContent = `Add ${config.singular}`;

  // lists needed to turn ids into names and to fill the drop-downs
  const lookups = {};
  async function loadLookups() {
    const needed = new Set(config.fields.filter((f) => typeof f.options === "string").map((f) => f.options));
    if (config.groups) needed.add("student-groups");
    for (const name of needed) lookups[name] = await api.get(`/api/${name}`);
  }
  function optionsFor(field) {
    if (Array.isArray(field.options)) return field.options;
    return (lookups[field.options] || []).map((r) => [r.id, r.name]);
  }
  function show(field, record) {
    const v = record[field.name];
    if (v === null || v === undefined || v === "") return "";
    if (field.kind === "checkbox") return v ? "Yes" : "No";
    if (field.kind === "select") {
      const found = optionsFor(field).find(([value]) => String(value) === String(v));
      return found ? found[1] : v;
    }
    return v;
  }

  let records = [];
  async function reload() {
    records = await api.get(`/api/${type}`);
    const table = el("table");
    const head = el("tr");
    for (const f of config.fields) head.appendChild(el("th", f.label.replace(" (optional)", "")));
    head.appendChild(el("th", "Actions"));
    table.appendChild(head);
    if (records.length === 0) {
      const tr = el("tr"); const td = el("td", `No ${config.title.toLowerCase()} yet.`); td.colSpan = config.fields.length + 1; tr.appendChild(td); table.appendChild(tr);
    }
    for (const record of records) {
      const tr = el("tr");
      for (const f of config.fields) tr.appendChild(el("td", String(show(f, record))));
      const actions = el("td");
      const edit = el("button", "Edit", "secondary"); edit.type = "button";
      edit.addEventListener("click", () => openForm(record));
      const del = el("button", "Delete", "danger"); del.type = "button"; del.style.marginLeft = "0.4rem";
      del.addEventListener("click", () => remove(record));
      actions.append(edit, del);
      tr.appendChild(actions);
      table.appendChild(tr);
    }
    const wrap = el("div", undefined, "scroll-x"); wrap.appendChild(table);
    area.replaceChildren(wrap);
  }

  async function remove(record) {
    const label = record.name || record.code || `#${record.id}`;
    if (!window.confirm(`Delete "${label}"? This cannot be undone.`)) return;
    try {
      await api.del(`/api/${type}/${record.id}`);
      say(`Deleted "${label}".`, "ok");
      await reload();
    } catch (err) { say(err.message, "error"); }
  }

  async function openForm(record) {
    const editing = Boolean(record);
    let currentGroups = [];
    if (config.groups && editing) currentGroups = (await api.get(`/api/courses/${record.id}/groups`)).group_ids;

    form.replaceChildren();
    form.appendChild(el("h2", editing ? `Edit ${config.singular}` : `Add ${config.singular}`));
    for (const f of config.fields) {
      const id = `f-${f.name}`;
      const label = el("label", f.label); label.htmlFor = id;
      let input;
      if (f.kind === "select") {
        input = el("select");
        if (!f.required) { const o = el("option", f.blank || "None"); o.value = ""; input.appendChild(o); }
        for (const [value, text] of optionsFor(f).filter(([value]) => !(editing && f.name === "parent_group_id" && value === record.id))) {
          const o = el("option", String(text)); o.value = value; input.appendChild(o);
        }
      } else if (f.kind === "checkbox") {
        input = el("input"); input.type = "checkbox";
      } else {
        input = el("input"); input.type = f.kind === "number" ? "number" : "text";
        if (f.kind === "number") input.min = 1;
      }
      input.id = id; input.name = f.name;
      if (f.required) input.required = true;
      const current = editing ? record[f.name] : f.default;
      if (f.kind === "checkbox") input.checked = Boolean(current);
      else if (current !== undefined && current !== null) input.value = current;
      form.append(label, input);
    }
    if (config.groups) {
      form.appendChild(el("label", "Student groups that take this course (at least one)"));
      const box = el("div", undefined, "checks"); box.id = "group-checks";
      for (const g of lookups["student-groups"] || []) {
        const l = el("label"); const c = el("input"); c.type = "checkbox"; c.value = g.id; c.checked = currentGroups.includes(g.id);
        l.append(c, document.createTextNode(" " + g.name)); box.appendChild(l);
      }
      form.appendChild(box);
    }
    const error = el("p", "", ""); error.id = "form-error"; error.setAttribute("role", "alert"); error.hidden = true;
    const actions = el("div", undefined, "actions");
    const cancel = el("button", "Cancel", "secondary"); cancel.type = "button"; cancel.addEventListener("click", () => dialog.close());
    const save = el("button", "Save"); save.type = "submit";
    actions.append(save, cancel);
    form.append(error, actions);

    form.onsubmit = async (event) => {
      event.preventDefault();
      error.hidden = true;
      const body = {};
      for (const f of config.fields) {
        const input = form.elements[f.name];
        if (f.kind === "checkbox") body[f.name] = input.checked ? 1 : 0;
        else if (f.kind === "number") body[f.name] = input.value === "" ? null : Number(input.value);
        else if (f.kind === "select") body[f.name] = input.value === "" ? null : (Number.isNaN(Number(input.value)) ? input.value : Number(input.value));
        else body[f.name] = input.value.trim();
      }
      const chosen = config.groups ? [...form.querySelectorAll("#group-checks input:checked")].map((c) => Number(c.value)) : [];
      if (config.groups && chosen.length === 0) { error.textContent = "Choose at least one student group."; error.hidden = false; return; }
      save.disabled = true;
      try {
        const saved = editing ? await api.put(`/api/${type}/${record.id}`, body) : await api.post(`/api/${type}`, body);
        if (config.groups) await api.put(`/api/courses/${saved.id}/groups`, { group_ids: chosen });
        dialog.close();
        say(`${editing ? "Saved" : "Added"} ${config.singular}.`, "ok");
        await reload();
      } catch (err) { error.textContent = err.message; error.hidden = false; }
      finally { save.disabled = false; }
    };
    dialog.showModal();
  }

  addButton.addEventListener("click", () => openForm(null));
  await loadLookups();
  await reload();
}
