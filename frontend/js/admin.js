// Drives admin/manage.html.  TODO (Ticket 3)
import { api } from "./api.js";

// One config per data type: which fields to show and edit. Keeps one page for all five.
export const TYPES = {
  "lecturers":      { title: "Lecturers",      fields: ["name", "email"] },
  "courses":        { title: "Courses",        fields: ["code", "name", "year_level", "lecturer_id", "weekly_hours", "block_hours"] },
  "rooms":          { title: "Rooms",          fields: ["name", "capacity", "room_type"] },
  "student-groups": { title: "Student groups", fields: ["name", "year_level", "size"] },
  "time-slots":     { title: "Time slots",     fields: ["day_of_week", "start_time", "end_time", "is_break"] },
};

export async function initManagePage() {
  // TODO (Ticket 3):
  //   1. read ?type= from the URL; look it up in TYPES (unknown type -> message + link home)
  //   2. api.get(`/api/${type}`) and render a table with Edit / Delete buttons
  //   3. "Add new" and "Edit" open #edit-dialog with a form built from TYPES[type].fields
  //   4. Save -> api.post / api.put, then reload the table; show server error text in #status
  //   5. Delete asks for confirmation first
}
