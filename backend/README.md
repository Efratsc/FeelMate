# FeelMate Backend

## 🚀 Quick Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy the template and update with your database credentials:
```bash
cp env.template .env
```

**IMPORTANT:** Update the `.env` file with your actual `DATABASE_URL` from your frontend configuration.

### 3. Run Database Setup
```bash
python setup_database.py
```

### 4. Start the Server
```bash
python chat_server.py
```

## 🔒 Security Notes

- **Never commit `.env` files to version control**
- The `.env` file is already in `.gitignore`
- Use `env.template` as a reference for required environment variables
- Keep your database credentials secure and private

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
