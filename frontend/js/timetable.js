
import { api } from "./api.js";

export const DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];

export const HOURS = [
  "08:15",
  "09:15",
  "10:15",
  "11:15",
  "12:15",
  "13:15",
  "14:15",
  "15:15"
]; // 12:15 = lunch

export function renderWeekGrid(entries, container) {
  const table = document.createElement("table");
  const header = document.createElement("tr");

  const timeHeading = document.createElement("th");
  timeHeading.textContent = "Time";
  header.appendChild(timeHeading);

  DAYS.forEach(day => {
    const heading = document.createElement("th");
    heading.textContent = day;
    header.appendChild(heading);
  });

  const thead = document.createElement("thead");
  thead.appendChild(header);
  table.appendChild(thead);

  const tbody = document.createElement("tbody");

  HOURS.forEach(hour => {
    const row = document.createElement("tr");
    const timeCell = document.createElement("th");

    timeCell.textContent = hour;
    row.appendChild(timeCell);

    if (hour === "12:15") {
      const lunchCell = document.createElement("td");
      lunchCell.colSpan = DAYS.length;
      lunchCell.textContent = "LUNCH BREAK";
      row.appendChild(lunchCell);
    } else {
      DAYS.forEach(day => {
        const cell = document.createElement("td");

        const lessons = entries.filter(entry =>
          entry.day === day &&
          String(entry.start_time || "").slice(0, 5) === hour
        );

        lessons.forEach(entry => {
          const course = document.createElement("strong");
          course.textContent =
            `${entry.course_code || ""} ${entry.course_name || ""}`.trim();

          const lecturer = document.createElement("p");
          lecturer.textContent =
            `Lecturer: ${entry.lecturer_name || "Not available"}`;

          const room = document.createElement("p");
          room.textContent =
            `Room: ${entry.room_name || "Not available"}`;

          cell.append(course, lecturer, room);
        });

        if (lessons.length === 0) {
          cell.textContent = "-";
        }

        row.appendChild(cell);
      });
    }

    tbody.appendChild(row);
  });

  table.appendChild(tbody);
  container.replaceChildren(table);
}

export function renderDayList(entries, day, container) {
  const heading = document.createElement("h2");
  heading.textContent = day;

  const list = document.createElement("ul");

  const dayEntries = entries
    .filter(entry => entry.day === day)
    .sort((a, b) =>
      String(a.start_time || "").localeCompare(String(b.start_time || ""))
    );

  if (dayEntries.length === 0) {
    const message = document.createElement("p");
    message.textContent = "No lessons scheduled for this day.";
    container.replaceChildren(heading, message);
    return;
  }

  dayEntries.forEach(entry => {
    const item = document.createElement("li");

    const course = document.createElement("strong");
    course.textContent =
      `${entry.course_code || ""} ${entry.course_name || ""}`.trim();

    const time = document.createElement("p");
    time.textContent = `Time: ${entry.start_time || "Not available"}`;

    const lecturer = document.createElement("p");
    lecturer.textContent =
      `Lecturer: ${entry.lecturer_name || "Not available"}`;

    const room = document.createElement("p");
    room.textContent = `Room: ${entry.room_name || "Not available"}`;

    item.append(course, time, lecturer, room);
    list.appendChild(item);
  });

  container.replaceChildren(heading, list);
}

export async function initTimetableView() {
  const container = document.getElementById("timetable-container");
  const emptyState = document.getElementById("empty-state");
  const weekButton = document.getElementById("week-button");
  const dayButton = document.getElementById("day-button");

  if (!container) {
    console.error("Timetable container not found.");
    return;
  }

  try {
    const response = await api.get("/api/timetables/published/mine");
    const data = response.data || response;
    const entries = data.entries || [];

    if (!data.published || entries.length === 0) {
      if (emptyState) {
        emptyState.hidden = false;
        emptyState.textContent = "No published timetable is available.";
      }

      container.replaceChildren();
      return;
    }

    if (emptyState) {
      emptyState.hidden = true;
    }

    const todayNumber = new Date().getDay();
    const today =
      todayNumber >= 1 && todayNumber <= 5
        ? DAYS[todayNumber - 1]
        : DAYS[0];

    const isNarrowScreen =
      window.matchMedia("(max-width: 600px)").matches;

    let currentView = isNarrowScreen ? "day" : "week";

    function showTimetable() {
      if (currentView === "day") {
        renderDayList(entries, today, container);
      } else {
        renderWeekGrid(entries, container);
      }
    }

    if (weekButton) {
      weekButton.addEventListener("click", () => {
        currentView = "week";
        showTimetable();
      });
    }

    if (dayButton) {
      dayButton.addEventListener("click", () => {
        currentView = "day";
        showTimetable();
      });
    }

    showTimetable();
  } catch (error) {
    if (emptyState) {
      emptyState.hidden = false;
      emptyState.textContent =
        error.message || "Could not load your timetable.";
    }

    container.replaceChildren();
  }
}
