# Deployment Guide: AI Counselling Platform 🚀

Your project is ready for deployment! You have already set up the **Database (Supabase)** and **Version Control (GitHub)**.

## 1. Prerequisites (Already Done ✅)
-   **GitHub Repo**: `https://github.com/yuganter98/AI-counselor`
-   **Database**: Supabase PostgreSQL (Connected & Seeded)

---

## 2. Deploy Backend (Render.com)

We will deploy the Python FastAPI backend first.

1.  **Create Account**: Log in to [dashboard.render.com](https://dashboard.render.com/).
2.  **New Web Service**: Click **New +** -> **Web Service**.
3.  **Connect GitHub**: Select your repo `AI-counselor`.
4.  **Configure Service**:
    -   **Name**: `ai-counsellor-backend`
    -   **Root Directory**: `backend` (Important!)
    -   **Runtime**: `Python 3`
    -   **Build Command**: `pip install -r requirements.txt`
    -   **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port 10000`
5.  **Environment Variables** (Copy these from your local `.env`):
    -   `PYTHON_VERSION`: `3.11.0` (Optional, good for stability)
    -   `POSTGRES_SERVER`: `aws-1-ap-northeast-1.pooler.supabase.com`
    -   `POSTGRES_PORT`: `6543`
    -   `POSTGRES_DB`: `postgres`
    -   `POSTGRES_USER`: `postgres.sybxvbsrsehxwywauwhe`
    -   `POSTGRES_PASSWORD`: `[YOUR_PASSWORD]` (The one you provided earlier: `CB...`)
    -   `SECRET_KEY`: `09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7`
6.  Click **Deploy Web Service**.
7.  **Wait**: Once deployed, copy the **URL** (e.g., `https://ai-counsellor-backend.onrender.com`).

---

## 3. Deploy Frontend (Vercel)

Now deploy the Next.js frontend.

1.  **Create Account**: Log in to [vercel.com](https://vercel.com/).
2.  **Add Project**: Click **Add New** -> **Project**.
3.  **Import Git Repository**: Select `AI-counselor`.
4.  **Configure Project**:
    -   **Framework Preset**: `Next.js` (Default)
    -   **Root Directory**: Click `Edit` and select `frontend`.
5.  **Environment Variables**:
    -   `NEXT_PUBLIC_API_URL`: Paste your **Render Backend URL** here (Add `/api/v1` at the end).
        -   Example: `https://ai-counsellor-backend.onrender.com/api/v1`
6.  Click **Deploy**.

---

## 4. Final Verification
-   Open your **Vercel URL**.
-   Try **Signing Up** (This verifies DB connection).
-   Try **Chatting with AI** (Verifies Backend logic).

**🎉 Your AI Counselling Platform is Live!**

---

## 5. Post-Deployment Security (Optional but Recommended)
By default, your backend allows connections from ANY website (`*`) to ensure easy setup.
To lock it down so **ONLY** your frontend can talk to your backend:

1.  Copy your final **Vercel Frontend URL** (e.g., `https://ai-counsellor-xyz.vercel.app`).
2.  Go to **Render Dashboard** -> Your Service -> **Environment**.
3.  Add a new Variable:
    -   Key: `BACKEND_CORS_ORIGINS`
    -   Value: `["https://ai-counsellor-xyz.vercel.app"]`
    *(Note: Keep the brackets and quotes)*
4.  Render will redeploy. Now your API is secure! 🔒
