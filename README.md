# 🇰🇷 Korean Language Course Registration Portal

A web application that allows users to browse current course announcements and sign up for Korean language learning groups. Built with a clean admin panel for easy content management.

---

## 📌 About the Project

This portal was developed to streamline the enrollment process for Korean language courses. Students can view available groups, read announcements, and register — all from one place. Administrators have a dedicated panel to manage courses, groups, and user registrations.

> 🤖 Architecture and code structure were optimized with the assistance of **Claude AI** (Anthropic).

---

## ⚙️ Tech Stack

| Layer      | Technology              |
|------------|-------------------------|
| Backend    | Python 3.x / Flask      |
| Database   | SQLite + Flask-SQLAlchemy |
| Frontend   | HTML5, CSS3, JavaScript |
| Templating | Jinja2                  |

---

## ✨ Features

- 📢 **Announcements** — view current news and updates from the school
- 📋 **Course Catalog** — browse available Korean language groups and levels
- ✍️ **Registration** — sign up for a group directly through the website
- 🔐 **Admin Panel** — manage announcements, courses, and enrollments
- 🗄️ **SQLite Database** — lightweight, file-based storage, no setup required

---

## 📁 Project Structure

```
korean-course-site/
├── backend/
│   ├── app.py               # Application entry point
│   ├── requirements.txt     # Python dependencies
│   ├── routes/
│   │   └── courses.py       # Course & registration route logic
│   └── models/
│       └── database.py      # Database models (Course, Lesson, User)
├── frontend/
│   ├── static/
│   │   ├── css/             # Stylesheets
│   │   └── js/              # JavaScript files
│   └── templates/
│       └── index.html       # Main page template
├── .gitignore
└── README.md
```

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/your-username/korean-course-site.git
cd korean-course-site
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r backend/requirements.txt
```

### 4. Run the application
```bash
python backend/app.py
```

### 5. Open in browser
```
http://127.0.0.1:5000
```

---

## 🛠️ Admin Panel

The admin panel is available at `/admin`. Use it to:
- Add or edit course announcements
- Create and manage course groups
- View and manage student registrations

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).

---

*Built with ❤️ and optimized with Claude AI*