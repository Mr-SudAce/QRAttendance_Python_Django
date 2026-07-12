# EduTrack QR — QR-Based Attendance System

Django web app for classroom attendance via QR codes. Three roles: **Student**, **Teacher**, **Superuser (admin)**.

## Stack

- **Backend:** Django 6.0.5, Python
- **DB:** SQLite (dev) — `psycopg2-binary` included, so Postgres-ready for prod
- **Frontend:** Django templates + Bootstrap 5.3.8 + Bootstrap Icons + custom CSS (`static/CSS/index.css`)
- **QR:** `qrcode` lib (`QRA_app/QR_generator.py`)
- **Tunneling:** `pyngrok` (likely for local demo/testing on real devices)
- **Auth:** Custom `User` model extending `AbstractUser` with `role` field (student/teacher/superuser)

## Project Structure

```
QRAttendance_Python_Django/
├── QRA_main/              # Django project settings, root urls, wsgi/asgi
├── QRA_app/
│   ├── auth/               # login/register/password-reset views + urls
│   ├── Views/              # views.py, course_view, department_views,
│   │                         students_views, teachers_views
│   ├── routes/              # per-domain urlpatterns (main, teacher, student,
│   │                         course, department)
│   ├── templates/
│   │   ├── auth/            # login/register/password reset pages
│   │   └── UI/
│   │       ├── teacher/     # dashboard, QR session, attendance history, profile
│   │       ├── student/     # dashboard, attendance history, profile
│   │       ├── department/  # dashboard, list, detail, add
│   │       ├── course/      # dashboard, list, detail, add, assign teacher
│   │       └── superadmin/  # dashboard
│   ├── models.py           # User, Department, Course, CourseAssignment,
│   │                         Enrollment, AttendanceSession, AttendanceRecord,
│   │                         DeviceLog, AttendanceSummary
│   ├── permission.py
│   ├── signals.py
│   ├── generate_username.py
│   └── QR_generator.py
├── static/
│   ├── CSS/index.css       # design tokens + shared component styles
│   └── logo/               # EDUQR logo variants
├── requirements.txt
├── manage.py
└── run.bat
```

## Data Model (core relations)

- `User` (role: student/teacher/superuser) → auto-sets role from `is_staff`/`is_superuser`
- `DepartmentModel` → has many `CourseModel`
- `CourseModel` → belongs to a department, has `CourseAssignment` (teacher) and `EnrollmentModel` (students)
- `AttendanceSessionModel` → one per class session, has a unique `session_token` (UUID) used to build the QR/scan URL, with `expires_at` + `is_active`
- `AttendanceRecordModel` → one row per student per session (`present`/`absent`), unique per (student, session)
- `DeviceLogModel` → tracks device hash per user (anti-proxy/spoofing check, presumably)
- `AttendanceSummaryModel` → cached `attendance_percentage` per (student, course)

**Flow:** Teacher starts a session → QR generated from `session_token` → student scans → hits `/student/scan/<token>` → attendance record created if session valid/not expired.

## Setup

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Needs a `.env` file (see `.gitignore` — already set up to keep it out of git). Uses `python-dotenv`.

## Current State / Notes

- Core backend (models, auth, role-based views, QR session flow) looks functionally complete.
- UI currently: Bootstrap 5 default components + one shared `index.css` with CSS variables (`--color-primary`, `--color-secondary`, etc.) — functional but generic/template-like, not yet visually distinctive.
- `base.html` is the shared layout (navbar + Bootstrap + messages/alerts block) — good foundation, all pages extend it.
- Templates are already well-organized by role/domain (teacher/student/department/course/superadmin) — makes a UI pass easy to scope page-by-page.

## Recent Feature Additions

### 1. Desktop ↔ Mobile QR Handoff (student dashboard)
Scanning a QR code with a laptop webcam is a bad experience, so the student dashboard now detects device type server-side (`is_mobile()` in `students_views.py`, user-agent check) and branches:
- **Desktop:** shows the *current* active session's QR code (generated in-memory as a base64 PNG via `generate_qr_base64()` in `QR_generator.py` — no file saved to disk), with a "Waiting for scan" status that polls `session_status` every 3s and flips to "Checked in" once the phone scan lands. Student logs into the same dashboard on their phone and scans the code shown on their own laptop screen.
- **Mobile:** unchanged — shows the existing camera scanner (`html5-qrcode`).
- New endpoint: `student/session/<id>/status/` (`session_status` view) — lightweight JSON polling, no page reload needed.
- **Known limitation:** desktop QR only appears for courses the student is already enrolled in. See roster feature below — this is now resolved as long as a teacher pre-enrolls the student.

### 2. Roster-Based Enrollment (security fix)
Previously, `submit_attendance` auto-enrolled *any* student in *any* course the instant they scanned a valid token (`EnrollmentModel.objects.get_or_create(...)`). That meant a leaked/screenshotted/shared QR code let anyone mark themselves present in a class they were never part of.

Fixed by flipping to roster-first:
- `submit_attendance` now checks `EnrollmentModel.objects.filter(student=student, course=session.course).exists()` and rejects the scan with a flash message if the student isn't already enrolled — no more silent self-enrollment.
- Teachers manage their own course rosters at `teacher/course/<course_id>/roster/` (new `manage_roster` / `enroll_student` / `remove_student` views + `manage_roster.html` template). Lookups are scoped to `courseassignment__teacher=request.user`, so a teacher can only manage rosters for courses they're actually assigned to.
- "Roster" button added to the course card on `teacher_dashboard.html`, next to Start/Details, matching existing card style.
- Django admin (`/admin/`) also works as a fallback roster tool since `EnrollmentModel` is already registered there.

## TODO / Ideas

- [ ] Visual redesign pass (see UI suggestions below)
- [ ] Handle first-time enrollment edge case: a brand-new student with zero enrollments won't see any desktop QR until a teacher adds them via the roster page (previously this happened automatically on first phone scan — now it's a manual step)
- [ ] Dashboard data viz (attendance charts) for teacher/superadmin views
- [ ] Verify `.env` was fully scrubbed from git history (was added in a later commit — check `git log -p .env`)
- [ ] Clean up leftover dead markup below `{% endblock %}` in `qr_session.html` (harmless, just unused)