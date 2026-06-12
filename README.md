# Student Profile Tracker API

A lightweight CRUD REST API for managing student records, built with **FastAPI**, **SQLModel**, and **PostgreSQL**.

---

## Tech Stack

- **FastAPI** — high-performance async web framework
- **SQLModel** — unified ORM + Pydantic validation layer
- **PostgreSQL** — relational database
- **Uvicorn** — ASGI server

---

## Project Structure

```
.
├── main.py        # FastAPI app, route definitions
├── models.py      # SQLModel table and update schemas
├── database.py    # Engine setup, session dependency
└── README.md
```

---

## Data Models

### `StudentRecord` (DB table + request schema)
| Field    | Type    | Notes               |
|----------|---------|---------------------|
| `id`     | int     | Auto-increment PK   |
| `name`   | str     | Required            |
| `branch` | str     | Required            |
| `cgpa`   | float   | Required            |

### `StudentUpdate` (partial update schema)
All fields optional — only provided fields are updated.

---

## API Endpoints

| Method   | Endpoint                        | Description                  | Status Code |
|----------|---------------------------------|------------------------------|-------------|
| `GET`    | `/`                             | Health check / welcome        | 200         |
| `POST`   | `/createStudent`                | Create a new student record   | 201         |
| `GET`    | `/getStudents`                  | Fetch all students            | 200         |
| `GET`    | `/getStudent/{student_id}`      | Fetch student by ID           | 200         |
| `PATCH`  | `/updateStudent/{student_id}`   | Partially update a student    | 200         |
| `DELETE` | `/delete_student/{student_id}`  | Delete a student record       | 204         |

---

## Local Setup

### Prerequisites

- Python 3.11+
- PostgreSQL

### 1. Clone the repository

```bash
git clone https://github.com/Vedant078/student-profile-tracker
cd student-profile-tracker
```

### 2. Install dependencies

```bash
pip install fastapi sqlmodel uvicorn psycopg2-binary
```

### 3. Create the database

```bash
createdb student_db
```

### 4. Configure the database URL

In `database.py`, update the connection string to match your local PostgreSQL setup:

```python
DATABASE_URL = "postgresql://localhost:5432/student_db"
```

On macOS with peer authentication, you may need:

```python
DATABASE_URL = "postgresql://localhost/student_db"
```

### 5. Run the server

```bash
uvicorn main:app --reload
```

The app will be available at `http://127.0.0.1:8000`.

---

## Interactive Docs

FastAPI auto-generates interactive API documentation:

- **Swagger UI** — `http://127.0.0.1:8000/docs`
- **ReDoc** — `http://127.0.0.1:8000/redoc`

---

## Example Requests

**Create a student**
```bash
curl -X POST "http://127.0.0.1:8000/createStudent" \
  -H "Content-Type: application/json" \
  -d '{"name": "Vedant", "branch": "Computer Science", "cgpa": 9.1}'
```

**Fetch all students**
```bash
curl "http://127.0.0.1:8000/getStudents"
```

**Update CGPA only**
```bash
curl -X PATCH "http://127.0.0.1:8000/updateStudent/1" \
  -H "Content-Type: application/json" \
  -d '{"cgpa": 9.5}'
```

**Delete a student**
```bash
curl -X DELETE "http://127.0.0.1:8000/delete_student/1"
```

---

## Key Design Decisions

- **2-model architecture** — `StudentRecord` doubles as both the DB table and the POST request body; `StudentUpdate` handles partial updates. No redundant intermediate schemas.
- **Lifespan context manager** — uses FastAPI's modern `@asynccontextmanager` lifespan pattern (replaces deprecated `on_event` hooks) to initialize the DB on startup.
- **Partial updates with `exclude_unset=True`** — `PATCH` only modifies fields explicitly provided in the request body, preventing accidental overwrites with `None`.