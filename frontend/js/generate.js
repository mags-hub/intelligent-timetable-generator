// Drives admin/generate.html.  TODO (Ticket 3, needs Ticket 6)
import { api } from "./api.js";

export async function initGeneratePage() {
  // TODO: see the four-step plan in generate.html.
  //   Generate -> api.post("/api/timetables/generate", {semester, academic_year})
  //   Preview  -> api.get(`/api/timetables/${id}`) then render with the grid from timetable.js
  //   Edit     -> api.put(`/api/timetables/${id}/entries/${entryId}`, {room_id, time_slot_id})
  //   Publish  -> api.post(`/api/timetables/${id}/publish`)
}
