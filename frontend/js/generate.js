
 // Drives admin/generate.html
import { api } from "./api.js";
import { renderWeekGrid } from "./timetable.js";

export async function initGeneratePage() {
  const form = document.getElementById("generate-form");
  const semesterInput = document.getElementById("semester");
  const yearInput = document.getElementById("year");
  const status = document.getElementById("status");
  const preview = document.getElementById("preview");
  const publishButton = document.getElementById("publish");

  const editForm = document.getElementById("edit-entry-form");
  const entryIdInput = document.getElementById("entry-id");
  const roomIdInput = document.getElementById("room-id");
  const slotIdInput = document.getElementById("slot-id");
  const editStatus = document.getElementById("edit-status");

  if (
    !form || !semesterInput || !yearInput ||
    !status || !preview || !publishButton
  ) {
    console.error("Some timetable generation HTML elements are missing.");
    return;
  }

  let timetableId = null;

  // Load and display a timetable.
  async function loadTimetable() {
    const response = await api.get(
      `/api/timetables/${timetableId}`
    );

    const timetable = response.data || response;
    const entries = timetable.entries || [];

    preview.replaceChildren();

    if (entries.length === 0) {
      status.textContent =
        "The timetable has no entries to display.";
      publishButton.hidden = true;
      return false;
    }

    renderWeekGrid(entries, preview);
    return true;
  }

  // Step 1: Generate the timetable.
  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const semester = Number(semesterInput.value);
    const year = Number(yearInput.value);

    if (![1, 2].includes(semester)) {
      status.textContent = "Please select semester 1 or 2.";
      return;
    }

    if (!Number.isInteger(year) || year < 2000 || year > 2100) {
      status.textContent = "Please enter a valid academic year.";
      return;
    }

    status.textContent = "Generating timetable...";
    preview.replaceChildren();
    publishButton.hidden = true;
    timetableId = null;

    try {
      const result = await api.post("/api/timetables/generate", {
        semester,
        academic_year: year
      });

      const generated = result.data || result;
      timetableId = generated.id || generated.timetable_id;

      if (!timetableId) {
        status.textContent =
          "Could not find the timetable ID in the server response.";
        return;
      }

      status.textContent = "Loading timetable preview...";

      const hasEntries = await loadTimetable();

      if (hasEntries) {
        status.textContent =
          "Timetable generated. Review it before publishing.";
        publishButton.hidden = false;
      }
    } catch (error) {
      status.textContent =
        error.message || "Could not generate the timetable.";
    }
  });

  // Step 2: Edit a room or time slot.
  if (editForm && entryIdInput && roomIdInput &&
      slotIdInput && editStatus) {
    editForm.addEventListener("submit", async (event) => {
      event.preventDefault();

      if (!timetableId) {
        editStatus.textContent =
          "Generate a timetable before editing entries.";
        return;
      }

      const entryId = Number(entryIdInput.value);
      const changes = {};

      if (roomIdInput.value.trim() !== "") {
        changes.room_id = Number(roomIdInput.value);
      }

      if (slotIdInput.value.trim() !== "") {
        changes.time_slot_id = Number(slotIdInput.value);
      }

      if (!Number.isInteger(entryId) || entryId <= 0 ||
          Object.keys(changes).length === 0 ||
          Object.values(changes).some(
            value => !Number.isInteger(value) || value <= 0
          )) {
        editStatus.textContent =
          "Enter a valid entry ID and a room ID or time-slot ID.";
        return;
      }

      editStatus.textContent = "Updating timetable entry...";

      try {
        await api.put(
          `/api/timetables/${timetableId}/entries/${entryId}`,
          changes
        );

        await loadTimetable();
        editStatus.textContent = "Timetable entry updated.";
      } catch (error) {
        if (error.status === 409 || error.statusCode === 409) {
          editStatus.textContent =
            "Clash detected. Choose another room or time slot. " +
            (error.message || "");
        } else {
          editStatus.textContent =
            error.message || "Could not update the timetable entry.";
        }
      }
    });
  }

  // Step 3: Publish the timetable.
  publishButton.addEventListener("click", async () => {
    if (!timetableId) {
      status.textContent = "Generate a timetable first.";
      return;
    }

    if (!confirm("Are you sure you want to publish this timetable?")) {
      return;
    }

    publishButton.disabled = true;
    status.textContent = "Publishing timetable...";

    try {
      await api.post(
        `/api/timetables/${timetableId}/publish`,
        {}
      );

      status.textContent = "Timetable published successfully.";
      publishButton.hidden = true;
    } catch (error) {
      status.textContent =
        error.message || "Could not publish the timetable.";
    } finally {
      publishButton.disabled = false;
    }
  });
}
