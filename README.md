# CUBAL — Connecting Unity for Blood and Life
### Blood & Plasma Donation Platform — Python + Flask Prototype

---

## How to run

```bash
# 1. Install dependencies
pip install flask pandas

# 2. Run the backend demo first (seeds the database)
python main.py

# 3. Start the web app
python app.py

# 4. Open browser → http://localhost:5000
```

---

## Project structure

```
cubal/
├── app.py                      ← Flask web app (run this for the UI)
├── main.py                     ← Terminal demo (seeds DB with sample data)
├── data/
│   ├── cubal.db                ← SQLite database (auto-created)
│   └── seed_data.py            ← Demo donors & recipients
├── models/
│   ├── database.py             ← DB connection + schema (5 tables)
│   ├── entities.py             ← OOP classes: Donor, Recipient, SOSRequest, etc.
│   └── repository.py           ← All DB read/write operations
├── services/
│   ├── registration.py         ← Donor/recipient sign-up logic
│   ├── sos_service.py          ← Full SOS lifecycle orchestration
│   ├── matching.py             ← Blood type + location matching engine
│   ├── notifications.py        ← SMS + in-app alert simulator
│   └── analytics.py            ← Pandas-based reports & audit trail
├── utils/
│   └── location.py             ← Haversine distance + radius filtering
├── templates/                  ← HTML pages (Jinja2)
│   ├── base.html
│   ├── index.html              ← Dashboard
│   ├── donors.html             ← Donor list
│   ├── register_donor.html     ← Donor sign-up form
│   ├── register_recipient.html ← Patient registration
│   ├── raise_sos.html          ← SOS request form
│   ├── requests.html           ← All SOS requests
│   ├── request_detail.html     ← Request + respond form + audit
│   └── audit.html              ← Full audit log
└── static/
    ├── css/style.css           ← CUBAL design system
    └── js/main.js              ← Live stats refresh
```

---

## Pages

| URL | Page |
|---|---|
| `/` | Dashboard — stats, open SOS requests, recent activity |
| `/register/donor` | Donor registration form |
| `/register/recipient` | Patient registration form |
| `/sos/raise` | Raise SOS — alerts all nearby donors immediately |
| `/donors` | All registered donors with availability |
| `/requests` | All SOS requests with status |
| `/requests/<id>` | Request detail + donor respond form + audit trail |
| `/audit` | Full system audit log |
| `/api/stats` | JSON stats endpoint (auto-refreshes dashboard) |

---

## Syllabus coverage

| Module | Where used |
|---|---|
| Python + OOP | `entities.py` — Donor, Recipient, SOSRequest, DonorResponse, AuditEntry |
| Encapsulation | Private state in dataclasses, `set_availability()`, `mark_fulfilled()` |
| Exception handling | `__post_init__` validation in all entity classes |
| File handling | SQLite DB file read/write |
| Data Structures | Hash map for blood-type index in `matching.py` |
| Algorithms | Haversine formula, radius-based search, sorted nearest-first |
| Time & space complexity | O(1) blood-type lookup via hash map vs O(n) linear scan |
| SQL / DBMS | 5 normalised tables, foreign keys, parameterised queries |
| Pandas / Data Science | Aggregations, value_counts, EDA in `analytics.py` |
| Web / Flask | Routes, templates, forms, flash messages, REST API endpoint |
| Design patterns | Repository pattern, Service layer, MVC separation |
