# ☁️ CloudVault — Secure Cloud File Management System

A full-stack, Google-Drive-style file manager built with **FastAPI (MVC)** + **React (Vite)** + **AWS S3**.
Files live in a **private S3 bucket** and are only reachable through short-lived **pre-signed URLs** issued after a database permission check. Folder structure, permissions, and trash live in the database; S3 stores opaque bytes under UUID keys.

---

## ✨ Features

- 🔐 JWT authentication (signup / login, bcrypt-hashed passwords)
- 📁 Folders & unlimited sub-folders (tree stored in DB)
- 📥 Drag-&-drop + multi-file upload (50 MB per file)
- ⚠️ Duplicate handling: **Replace** or **Keep both** → `new file (1).docx`, `new file (2).docx`
-  Move / ⧉ Copy / ✏️ Rename / 🗑 Delete with **Trash + Restore**
- 🔍 Search + sort by **name** or **date**, grid & list views
- 🔗 Share by email — only the owner or the exact shared email can open the item;
  sharing a **folder** grants access to everything inside it
- ⬇️ Downloads keep the **exact original filename** (Content-Disposition on signed URL)
- 📱 Fully responsive UI (mobile sidebar, adaptive grid), works over LAN

---

## 🧱 Tech Stack

| Layer     | Technology |
|-----------|------------|
| Backend   | FastAPI (MVC: models / views / controllers + services), SQLAlchemy |
| Database  | SQLite (dev) / PostgreSQL (prod-ready) |
| Storage   | AWS S3 (private bucket, boto3, pre-signed URLs) |
| Auth      | JWT (`python-jose`) + `bcrypt` via `passlib` |
| Frontend  | React 18 + Vite + Tailwind CSS v3, React Router, Axios |

---

## 📁 Project Structure

```
CloudVault/
├── backend/
│   ├── run.py                     # Uvicorn entry point
│   ├── requirements.txt
│   ├── .env.example
│   └── app/
│       ├── main.py                # App factory, CORS, routers
│       ├── config.py              # Env settings
│       ├── database.py            # SQLAlchemy engine/session
│       ├── models/                # [M]  User, Item, ItemShare
│       ├── views/                 # [V]  Pydantic schemas
│       ├── services/              # Business logic + S3 adapter
│       │   ├── auth_service.py
│       │   ├── file_service.py
│       │   └── s3_service.py
│       └── controllers/           # [C]  API routers
│           ├── auth_controller.py
│           └── file_controller.py
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js             # server.host: true (LAN access)
│   ├── tailwind.config.cjs        # content globs → all component folders
│   ├── postcss.config.cjs
│   ├── .env.example
│   └── src/  (or root-level app folders — see tailwind.config.cjs)
│       ├── api/axios.js           # baseURL from VITE_API_URL (+ LAN fallback)
│       ├── context/               # AuthContext, ToastContext
│       ├── hooks/useFiles.js      # All file state + API actions
│       ├── components/            # layout / files / modals / common
│       └── pages/                 # AuthPage, FileManagerPage
└── README.md
```

---

## ✅ Prerequisites

- **Python 3.10+** — `python --version`
- **Node.js 18+** — `node --version`
- **AWS account** (free tier is enough: 5 GB / 12 months)

---

## 🪣 Step 1 — AWS S3 Setup (one-time)

1. **Create bucket**: AWS Console → S3 → *Create bucket*
   - Name: e.g. `cloudvault-files` (globally unique)
   - Keep **Block all public access ✅ ON**
   - Default encryption (SSE-S3) is fine
2. **Create IAM user**: IAM → Users → *Create user* → `cloudvault-app` (no console access)
3. **Attach this inline policy** (IAM → Policies → Create policy → JSON):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "CloudVaultBucketOnly",
      "Effect": "Allow",
      "Action": ["s3:PutObject", "s3:GetObject", "s3:DeleteObject", "s3:ListBucket"],
      "Resource": [
        "arn:aws:s3:::YOUR-BUCKET-NAME",
        "arn:aws:s3:::YOUR-BUCKET-NAME/*"
      ]
    }
  ]
}
```

4. **Create access key**: user → *Security credentials* → *Create access key* →
   copy **Access Key ID** and **Secret Access Key**.

---

## 🔧 Step 2 — Backend

```bash
cd backend

# 1. Virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
copy .env.example .env         # Windows
# cp .env.example .env         # macOS / Linux
#    → open .env and fill in your AWS keys, bucket, region, JWT secret

# 4. Run
python run.py
```

✅ Backend: `http://localhost:8000` · 📖 Swagger docs: `http://localhost:8000/docs` · ❤️ Health: `/api/health`

### Backend `.env` reference

| Variable | Example | Purpose |
|---|---|---|
| `JWT_SECRET_KEY` | `long-random-string` | Signs JWTs — change it! |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Token lifetime |
| `DATABASE_URL` | `sqlite:///./cloudvault.db` | DB location (relative to `backend/`) |
| `AWS_ACCESS_KEY_ID` | `AKIA…` | IAM user key |
| `AWS_SECRET_ACCESS_KEY` | `…` | IAM user secret |
| `AWS_REGION` | `us-east-1` | Bucket region |
| `S3_BUCKET_NAME` | `cloudvault-files` | Your bucket |
| `ALLOWED_ORIGINS` | `http://localhost:5173` | CORS allow-list (comma-separated) |

---

## 🎨 Step 3 — Frontend

```bash
cd frontend

npm install

copy .env.example .env         # Windows  (cp on macOS/Linux)
#    → VITE_API_URL=http://localhost:8000
#    → (or leave unset to auto-detect host — useful for phone/LAN testing)

npm run dev
```

✅ Frontend: `http://localhost:5173` (Vite prints the exact URL — use it)

---

## 🚀 Run Everything

Open **two terminals**:

| Terminal | Command | Result |
|---|---|---|
| 1 | `cd backend && python run.py` | API on :8000 |
| 2 | `cd frontend && npm run dev` | UI on :5173 |

Then open `http://localhost:5173`, **Sign Up**, and start using it.

### Quick test flow
1. Sign up → auto-login → File Manager
2. Drag & drop a file → green toast + card appears
3. Drop the same file again → **Replace / Keep both** modal
4. `⋮` menu → Share → enter a second account's email
5. Log in as that account → **Shared with me** → open folder/file, download
6. Delete → **Trash** → Restore
7. 📱 Phone on same Wi-Fi: `ipconfig` → open `http://<PC-IP>:5173`

---

## 🔌 API Overview

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/auth/signup` · `/api/auth/login` | Register / get JWT |
| GET  | `/api/auth/me` | Current user |
| POST | `/api/files/folders` | Create folder/sub-folder |
| GET  | `/api/files/{parent_id}` | List folder (`0` = root), `?search=&sort_by=` |
| POST | `/api/files/upload/{parent_id}?conflict_action=replace\|rename` | Upload |
| GET  | `/api/files/shared` · `/recent` · `/trash` | Views |
| GET  | `/api/files/folder-options` | Targets for Move modal |
| POST | `/api/files/{id}/rename` · `/move` · `/copy` | Mutations |
| DELETE | `/api/files/{id}` | Soft-delete → Trash |
| POST | `/api/files/{id}/restore` | Restore from Trash |
| DELETE | `/api/files/{id}/permanent` | Hard delete (S3 + DB) |
| POST | `/api/files/{id}/share` · DELETE `/share/{email}` | Manage sharing |
| GET  | `/api/files/{id}/download` | 15-min pre-signed S3 URL |

---

## 🔐 Security Model

- Bucket is **private**; no public URLs, no bucket policy — access only via IAM keys + pre-signed URLs (15 min, single object)
- Every request: JWT → owner check **or** `item_shares` row (folder shares inherit to children via ancestor walk)
- bcrypt password hashing; identical login error for wrong email/password (no user enumeration)
- Least-privilege IAM policy scoped to one bucket
- CORS restricted to known origins (regex only for local/LAN dev)
- Upload size capped (50 MB); inputs validated by Pydantic at the boundary
- Rate Limiting
- JWT Revocation

---

## 📜 License

Personal / educational project — free to use and modify.
