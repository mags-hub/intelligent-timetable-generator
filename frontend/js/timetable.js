// Drives view/timetable.html.  TODO (Ticket 4, needs Tickets 5 and 6)
import { api } from "./api.js";

export const DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];
export const HOURS = ["08:15", "09:15", "10:15", "11:15", "12:15", "13:15", "14:15", "15:15"]; // 12:15 = lunch

export function renderWeekGrid(entries, container) {
  // TODO (Ticket 4): build a table, rows = HOURS, columns = DAYS. Each cell shows
  //   course code + name, lecturer, room. Draw 12:15 as a LUNCH row. Reused by admin/generate.html.
}

export function renderDayList(entries, day, container) {
  // TODO (Ticket 4): simple list for one day; this is the phone-friendly view.
}

export async function initTimetableView() {
  // TODO (Ticket 4):
  //   data = await api.get("/api/timetables/published/mine")
  //   if (!data.published || data.entries.length === 0) -> show #empty-state and stop
  //   otherwise render the week grid (wide screens) or today's list (narrow screens),
  //   and wire the Week / Day toggle buttons.
}
