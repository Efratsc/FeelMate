# FeelMate Backend

## 🚀 Quick Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables (SECURE)
Run the secure setup script:
```bash
python secure_setup.py
```

**Then manually edit the `.env` file:**
- Open `.env` in your editor
- Replace `your_database_url_here` with your actual `DATABASE_URL`
- Copy the `DATABASE_URL` from your frontend `.env` file

### 3. Run Database Setup
```bash
python setup_database.py
```

### 4. Start the Server
```bash
python chat_server.py
```

## 🔒 Security Notes

- **✅ No credentials exposed in code** - All sensitive data is in `.env` files only
- **✅ .env files are gitignored** - Won't be pushed to GitHub
- **✅ Template-based setup** - Users provide their own credentials
- **✅ Secure by default** - No hardcoded database URLs

## 📡 API Endpoints

- **Health Check:** `GET /health`
- **Chat Message:** `POST /api/chat/send-message`
- **Chat History:** `GET /api/chat/history/{session_id}`
- **Dashboard Stats:** `GET /api/analytics/dashboard-stats`

## 🗄️ Database

The backend connects to the same PostgreSQL database as the frontend for:
- Chat session management
- Message history storage
- User conversation context
