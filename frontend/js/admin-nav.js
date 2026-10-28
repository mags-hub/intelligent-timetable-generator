
export function loadAdminNav(navElement) {
  navElement.innerHTML = `
    <a href="dashboard.html">Dashboard</a>
    <a href="manage.html?type=lecturers">Lecturers</a>
    <a href="manage.html?type=courses">Courses</a>
    <a href="manage.html?type=rooms">Rooms</a>
    <a href="manage.html?type=student-groups">Student groups</a>
    <a href="manage.html?type=time-slots">Time slots</a>
    <a href="generate.html">Generate timetable</a>
    <button id="logout" type="button">Sign out</button>
  `;
}
