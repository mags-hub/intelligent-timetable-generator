# frontend/  (Tickets 3 and 4)

Plain HTML, CSS and JavaScript, no build step. During development Flask serves this folder
at the site root, so run `python backend/run.py` and open `http://127.0.0.1:5000/login.html`.
Pages and API share one address, so `fetch("/api/...")` just works. Opening the HTML files
straight from disk will NOT work.

```
frontend/
├── index.html            redirects to login or the right home page by role
├── login.html            login form                                       [Ticket 3]
├── admin/
│   ├── dashboard.html    admin home with links to every section           [Ticket 3]
│   ├── manage.html       ONE page that manages any data type via ?type=   [Ticket 3]
│   └── generate.html     generate, preview, edit, publish a timetable     [Ticket 3]
├── view/
│   └── timetable.html    read-only weekly/daily view, lecturer + student  [Ticket 4]
├── css/styles.css        shared tokens and layout (small, extend as needed)
└── js/
    ├── api.js            fetch wrapper: all backend calls go through here  [done]
    ├── auth.js           login, logout, role redirects                     [Ticket 3]
    ├── admin.js          drives manage.html                                [Ticket 3]
    ├── generate.js       drives generate.html                              [Ticket 3]
    └── timetable.js      drives view/timetable.html                        [Ticket 4]
```

## Who builds what

- **Ticket 3 (admin shell):** login page, dashboard navigation, and the management screens for
  lecturers, courses, rooms, student groups and time slots. Start with mock data in `js/api.js`
  (`USE_MOCK = true`), then switch it off once Ticket 6 endpoints exist.
- **Ticket 4 (timetable views):** weekly and daily grid, mobile friendly, with a friendly
  "No timetable has been published yet" state. Needs Tickets 5 and 6.
- **Not in the original tickets but needed:** `admin/generate.html`, where the admin runs
  the generator, reviews the result, fixes clashes by hand and publishes. Assign it with Ticket 3.

## Rules of the road

- Never call `fetch` directly in a page script. Use `api.get/post/put/del` so errors,
  login redirects and the mock switch work everywhere.
- The timetable grid comes from the real Richfield layout: Mon to Fri, 08:15 to 16:15,
  one-hour rows, 12:15 to 13:15 shown as LUNCH.
- Show database error messages (409 clash reasons) to the admin in plain words.
- Visual design is open: the CSS file only holds a small set of colour and spacing variables.
  Pick a look together with the team and apply it in `styles.css` so all pages stay consistent.
- Keep it accessible: labels on every input, visible keyboard focus, works at phone width.
