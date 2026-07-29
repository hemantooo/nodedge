# 🍎 Apple + AIML Workshop Registration Portal

A full-stack workshop registration platform built for **Parul University's Apple + AIML event**. Students can register through a sleek Next.js frontend, and their data is validated and synced to Google Sheets via a FastAPI backend.

---

## 📁 Project Structure

```text
apple+aiml-event/
├── backend/                  # FastAPI Python Backend
│   ├── main.py               # App entry point (CORS, validation, endpoints)
│   ├── schemas.py            # Pydantic schemas (email domain validation)
│   ├── sheets_service.py     # Google Sheets integration (gspread)
│   ├── test_main.py          # Pytest unit tests
│   ├── requirements.txt      # Python dependencies
│   ├── .env.example          # Environment variables template
│   └── credentials.json      # ⛔ NOT committed (add your own)
│
├── frontend/                 # Next.js + Tailwind CSS Frontend
│   ├── src/
│   │   ├── app/              # Next.js App Router pages
│   │   └── components/       # Reusable UI components
│   ├── package.json          # Node dependencies
│   ├── .env.example          # Frontend env template
│   └── ...
│
├── .gitignore
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+**
- **Node.js 18+** & **npm**
- A **Google Cloud Service Account** with Sheets API enabled ([guide](https://docs.gspread.org/en/latest/oauth2.html#for-bots-using-service-account))

---

### 1️⃣ Backend Setup

```bash
cd backend

# Create & activate virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Google Sheet ID and credentials path

# Place your Google service account JSON file as:
#   backend/credentials.json

# Run the server
uvicorn main:app --reload --port 8000
```

- **API Base**: `http://localhost:8000`
- **Swagger Docs**: `http://localhost:8000/docs`

---

### 2️⃣ Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local
# Edit .env.local if your backend runs on a different URL

# Run the dev server
npm run dev
```

- **Frontend**: `http://localhost:3000`

---

## 📡 API Endpoints

### `POST /api/register`

Register a student for the workshop.

**Request Body:**
```json
{
  "full_name": "John Doe",
  "enrollment_no": "210303123001",
  "email": "john.doe@paruluniversity.ac.in",
  "semester": "Semester 5",
  "proficiency": "Intermediate",
  "has_mac": true
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Registration successful!",
  "registration_id": "a1b2c3d4e5f67890"
}
```

### `GET /api/health`

Health check for backend + Google Sheets connectivity.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "total_registrations": 42,
  "google_sheets_connected": true,
  "message": null
}
```

---

## 🧪 Running Tests

```bash
cd backend
source venv/bin/activate
pytest test_main.py -v
```

---

## 🔐 Environment Variables

### Backend (`backend/.env`)

| Variable | Description |
|---|---|
| `GOOGLE_SHEETS_SPREADSHEET_ID` | Your Google Sheet ID (from the URL) |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | Path to service account JSON (`credentials.json`) |
| `PORT` | Server port (default: `8000`) |
| `HOST` | Server host (default: `0.0.0.0`) |

### Frontend (`frontend/.env.local`)

| Variable | Description |
|---|---|
| `NEXT_PUBLIC_BACKEND_URL` | Backend API URL (default: `http://localhost:8000`) |

---

## 🛡️ Security Notes

> ⚠️ **Never commit secrets to Git!**
>
> - `backend/.env` — contains your Sheet ID
> - `backend/credentials.json` — contains your Google service account private key
> - `frontend/.env.local` — may contain production URLs
>
> All of these are listed in `.gitignore` and will **not** be pushed.

---

## 📄 License

MIT
