# AI Counselling Platform 🎓

A comprehensive, AI-driven study abroad counselling platform that guides students from profile creation to university application.

## 🚀 Features

### 🤖 AI-Powered Guidance
-   **Smart Reasoning Engine**: Analyzes user profile (GPA, Budget, Exams) to provide personalized feedback.
-   **Actionable Advice**: Suggests specific next steps (e.g., "Improve IELTS", "Shortlist Universities").
-   **Interactive Chat**: Dedicated AI Counsellor interface for Q&A and command execution.

### 📊 Student Dashboard
-   **Profile Analysis**: Visual strength indicator (Weak/Average/Strong) with deep-dive breakdown.
-   **Stage Management**: Guided progression system (Profile -> Discovery -> Finalize -> Application).
-   **University Shortlisting**: Search, Filter, and Lock dream universities.
-   **Task Tracker**: Automated tasks generated based on target universities and application status.

### 🛠 Technical Highlights
-   **Neo-Brutalist UI**: Modern, high-contrast aesthetics using Tailwind CSS & Lucide React.
-   **Full-Stack Architecture**: Next.js (React) Frontend + FastAPI (Python) Backend.
-   **Cloud Database**: Production-ready PostgreSQL (Supabase) integration.

## 🔐 Security & Privacy

We prioritize student data security with industry-standard practices:

-   **JWT Authentication**: Stateless, secure session management with expiration control.
-   **Password Encryption**: Strong hashing algorithms (Bcrypt) to protect credentials.
-   **Role-Based Access Control (RBAC)**: Strict API guards ensuring users can only access their own data.
-   **Protected Routes**: Frontend middleware to prevent unauthorized access to dashboard pages.
-   **CORS Protection**: Whitelisted origins to prevent cross-site scripting attacks.
-   **Secure Envirionment**: Sensitive keys managed via `.env` files (not omitted in version control).

## 📦 Deployment

-   **Frontend**: Vercel
-   **Backend**: Render / Railway
-   **Database**: Supabase (PostgreSQL)

## 🏃‍♂️ Running Locally

### Backend
```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
pnpm install
pnpm next dev
```

---
*Built with ❤️ by Yuganter*
