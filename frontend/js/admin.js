
import { api } from "./api.js";

// Fields used for each type of data
export const TYPES = {
  "lecturers": {
    title: "Lecturers",
    fields: ["name", "email"]
  },
  "courses": {
    title: "Courses",
    fields: ["code", "name", "year_level", "lecturer_id", "weekly_hours", "block_hours"]
  },
  "rooms": {
    title: "Rooms",
    fields: ["name", "capacity", "room_type"]
  },
  "student-groups": {
    title: "Student groups",
    fields: ["name", "year_level", "size"]
  },
  "time-slots": {
    title: "Time slots",
    fields: ["day_of_week", "start_time", "end_time", "is_break"]
  }
};

export async function initManagePage() {
  const params = new URLSearchParams(window.location.search);
  const type = params.get("type");
  const config = TYPES[type];

  const title = document.getElementById("page-title");
  const addButton = document.getElementById("add-button");
  const status = document.getElementById("status");
  const tableArea = document.getElementById("table-area");
  const dialog = document.getElementById("edit-dialog");
  const form = document.getElementById("edit-form");

  // Check that the selected type exists
  if (!config) {
    title.textContent = "Unknown data type";
    status.textContent = "Please select a section from the admin menu.";
    tableArea.innerHTML = '<a href="dashboard.html">Back to dashboard</a>';
    addButton.disabled = true;
    return;
  }

  title.textContent = config.title;

  let editingId = null;

  // Load and display records
  async function loadRecords() {
    status.textContent = "Loading...";
    tableArea.innerHTML = "";

    try {
      const response = await api.get(`/api/${type}`);

      const records = Array.isArray(response)
        ? response
        : response.data || response.items || [];

      const table = document.createElement("table");
      const header = document.createElement("tr");

      for (const field of config.fields) {
        const th = document.createElement("th");
        th.textContent = field.replaceAll("_", " ");
        header.appendChild(th);
      }

      const actionsHeading = document.createElement("th");
      actionsHeading.textContent = "Actions";
      header.appendChild(actionsHeading);

      table.appendChild(header);

      records.forEach((record) => {
        const row = document.createElement("tr");

        config.fields.forEach((field) => {
          const cell = document.createElement("td");
          cell.textContent = record[field] ?? "";
          row.appendChild(cell);
        });

        const actions = document.createElement("td");

        const editButton = document.createElement("button");
        editButton.type = "button";
        editButton.textContent = "Edit";
        editButton.addEventListener("click", () => openForm(record));
        actions.appendChild(editButton);

        const deleteButton = document.createElement("button");
        deleteButton.type = "button";
        deleteButton.textContent = "Delete";

        deleteButton.addEventListener("click", async () => {
          if (!confirm("Are you sure you want to delete this record?")) {
            return;
          }

          try {
            await api.delete(`/api/${type}/${record.id}`);
            status.textContent = "Record deleted successfully.";
            await loadRecords();
          } catch (error) {
            status.textContent = error.message || "Could not delete record.";
          }
        });

        actions.appendChild(deleteButton);
        row.appendChild(actions);
        table.appendChild(row);
      });

      tableArea.appendChild(table);

      if (records.length === 0) {
        status.textContent = "No records found. Click Add new to create one.";
      } else {
        status.textContent = "";
      }
    } catch (error) {
      status.textContent = error.message || "Could not load records.";
    }
  }

  // Create the form for adding or editing a record
  function openForm(record = null) {
    editingId = record ? record.id : null;
    form.innerHTML = "";

    for (const field of config.fields) {
      const label = document.createElement("label");
      label.textContent = field.replaceAll("_", " ");

      const input = document.createElement("input");
      input.name = field;

      if (field === "is_break") {
        input.type = "checkbox";
        input.checked = record ? Boolean(record[field]) : false;
      } else {
        input.type = field === "email" ? "email" : "text";
        input.value = record && record[field] != null
          ? record[field]
          : "";

        if (field !== "lecturer_id") {
          input.required = true;
        }
      }

      label.appendChild(input);
      form.appendChild(label);
      form.appendChild(document.createElement("br"));
    }

    // Use a normal submit button so the form does not close before saving
    const saveButton = document.createElement("button");
    saveButton.type = "submit";
    saveButton.textContent = record ? "Save changes" : "Add record";
    form.appendChild(saveButton);

    dialog.showModal();
  }

  // Open the form when Add new is clicked
  addButton.addEventListener("click", () => openForm());

  // Save a new record or update an existing one
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    status.textContent = "";

    const record = {};

    for (const field of config.fields) {
      const input = form.elements.namedItem(field);

      record[field] = input.type === "checkbox"
        ? input.checked
        : input.value.trim();
    }

    try {
      if (editingId !== null) {
        await api.put(`/api/${type}/${editingId}`, record);
        status.textContent = "Record updated successfully.";
      } else {
        await api.post(`/api/${type}`, record);
        status.textContent = "Record added successfully.";
      }

      dialog.close();
      await loadRecords();
    } catch (error) {
      status.textContent = error.message || "Could not save record.";
    }
  });

  // Add a Cancel button inside the dialog
  const cancelButton = document.createElement("button");
  cancelButton.type = "button";
  cancelButton.textContent = "Cancel";
  cancelButton.addEventListener("click", () => dialog.close());
  form.appendChild(cancelButton);

  await loadRecords();
}
