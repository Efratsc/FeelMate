# Authentication Integration for FeelMate

## Overview

This document describes the complete authentication integration implemented for FeelMate, including user session management, secure API endpoints, and frontend authentication flow.

## 🔐 Authentication System

### Frontend Authentication (better-auth)

**Location**: `frontend/app/lib/auth.ts`

The frontend uses better-auth for user authentication with the following features:
- Email and password authentication
- PostgreSQL database integration
- Session management
- Secure cookie-based sessions

```typescript
// Configuration
export const auth = betterAuth({
  emailAndPassword: {
    enabled: true, 
  },
  database: new Pool({
    connectionString: process.env.DATABASE_URL,
  }),
});
```

### Backend User Session Management

**Location**: `backend/user_session.py`

The backend includes a comprehensive user session management system:

#### Key Features:
- ✅ **User Validation**: Validates user existence and session ownership
- ✅ **Session Tracking**: Manages chat sessions per user
- ✅ **History Management**: Retrieves user's chat history
- ✅ **Cleanup Utilities**: Removes expired sessions

#### Core Methods:

```python
# Validate user session
user_validation = user_session_manager.validate_user_session(
    user_id=user_id,
    session_id=session_id
)

# Get user's chat history
sessions = user_session_manager.get_user_chat_history(
    user_id=user_id, 
    limit=20
)

# Clean up expired sessions
cleaned_count = user_session_manager.cleanup_user_sessions(
    user_id=user_id, 
    timeout_hours=24
)
```

## 🚀 API Endpoints

### Protected Chat Endpoint

**Endpoint**: `POST /api/chat/send-message`

**Authentication**: Required
**Validation**: User session validation

```json
// Request
{
  "message": "I'm feeling sad today",
  "user_id": "authenticated_user_id",
  "session_id": "optional_session_id"
}

// Response
{
  "response": "I'm sorry you're feeling sad...",
  "emotion": "sadness",
  "severity": "low",
  "crisis_detected": false,
  "session_id": "session-123",
  "user_info": {
    "user_id": "user_123",
    "email": "user@example.com"
  }
}
```

### User Sessions Endpoint

**Endpoint**: `GET /api/chat/sessions/{user_id}`

**Authentication**: Required
**Purpose**: Get user's chat session history

```json
// Response
{
  "user_id": "user_123",
  "user_email": "user@example.com",
  "active_sessions": [
    {
      "session_id": "session-123",
      "created_at": "2025-01-20T10:00:00",
      "last_activity": "2025-01-20T11:30:00",
      "current_emotion": "sadness",
      "severity_level": "low",
      "message_count": 15,
      "recent_messages": [...]
    }
  ],
  "total_sessions": 5
}
```

### Session Cleanup Endpoint

**Endpoint**: `POST /api/chat/cleanup-user-sessions/{user_id}`

**Authentication**: Required
**Purpose**: Clean up expired sessions for a specific user

```json
// Response
{
  "message": "Cleaned up 3 expired sessions",
  "user_id": "user_123",
  "cleaned_count": 3,
  "status": "success"
}
```

## 🎨 Frontend Components

### AuthGuard Component

**Location**: `frontend/components/AuthGuard.jsx`

Protects routes and handles authentication state:

```jsx
<AuthGuard requireAuth={true}>
  <ProtectedComponent />
</AuthGuard>
```

**Features**:
- ✅ Automatic redirect to sign-in if not authenticated
- ✅ Loading states during authentication check
- ✅ Configurable authentication requirements

### UserProfile Component

**Location**: `frontend/components/UserProfile.jsx`

Displays user information and session management:

**Features**:
- ✅ User information display (email, user ID)
- ✅ Sign out functionality
- ✅ Chat session history
- ✅ Session cleanup tools
- ✅ Real-time session management

### Updated ChatBox Component

**Location**: `frontend/components/ChatBox.jsx`

Enhanced with authentication integration:

**Features**:
- ✅ Uses authenticated user ID
- ✅ Authentication state validation
- ✅ User info display in header
- ✅ Proper error handling for unauthenticated users

## 🔄 Authentication Flow

### 1. User Sign-In
```
User → Sign In Page → better-auth → PostgreSQL → Session Cookie
```

### 2. Protected Route Access
```
User → AuthGuard → Check Session → Redirect or Allow Access
```

### 3. Chat Request
```
Frontend → API Request → User Validation → Chatbot → Response
```

### 4. Session Management
```
User → UserProfile → Session History → Cleanup → Database Update
```

## 🛡️ Security Features

### Backend Security
- ✅ **User Validation**: Every API request validates user existence
- ✅ **Session Ownership**: Ensures sessions belong to authenticated users
- ✅ **Session Expiration**: Automatic cleanup of expired sessions
- ✅ **Error Handling**: Proper error responses for authentication failures

### Frontend Security
- ✅ **Route Protection**: AuthGuard prevents unauthorized access
- ✅ **Session Management**: Secure session handling with better-auth
- ✅ **User Isolation**: Each user only sees their own data
- ✅ **Automatic Redirects**: Redirects unauthenticated users to sign-in

## 📊 Database Schema

### Users Table (better-auth)
```sql
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- other better-auth fields
);
```

### Chat Sessions Table
```sql
CREATE TABLE chat_sessions (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id),
    session_id TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    current_emotion TEXT,
    severity_level TEXT,
    is_active BOOLEAN DEFAULT TRUE
);
```

### Chat Messages Table
```sql
CREATE TABLE chat_messages (
    id SERIAL PRIMARY KEY,
    session_id TEXT NOT NULL REFERENCES chat_sessions(session_id),
    message TEXT NOT NULL,
    sender TEXT NOT NULL,
    emotion TEXT,
    severity TEXT,
    confidence FLOAT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🚀 Usage Examples

### 1. Start the Application

```bash
# Backend
cd backend
python start_production.py

# Frontend
cd frontend
npm run dev
```

### 2. User Authentication Flow

1. **Sign Up**: User creates account at `/sign-up`
2. **Sign In**: User signs in at `/sign-in`
3. **Access Chat**: User is redirected to `/chat`
4. **Start Chatting**: User can now chat with FeelMate

### 3. Session Management

1. **View Sessions**: Click "Show Sessions" in UserProfile
2. **Refresh Sessions**: Click "Refresh" to get latest data
3. **Cleanup Sessions**: Click "Cleanup Old Sessions" to remove expired ones

## 🔧 Configuration

### Environment Variables

**Frontend** (`.env.local`):
```bash
DATABASE_URL=postgresql://username:password@localhost:5432/feelmate_db
NEXTAUTH_SECRET=your-secret-key
```

**Backend** (`.env`):
```bash
DATABASE_URL=postgresql://username:password@localhost:5432/feelmate_db
LOG_LEVEL=info
```

## 🐛 Troubleshooting

### Common Issues

1. **422 Unprocessable Entity**
   - **Cause**: Missing `user_id` in request
   - **Solution**: Ensure user is authenticated and `user_id` is included

2. **401 Authentication Failed**
   - **Cause**: Invalid user ID or expired session
   - **Solution**: Re-authenticate user

3. **Database Connection Errors**
   - **Cause**: Invalid DATABASE_URL or database not running
   - **Solution**: Check database connection and credentials

### Debug Mode

Enable debug logging in backend:
```python
# In config.py
LOG_LEVEL = "debug"
```

## 📈 Future Enhancements

### Planned Features
1. **Multi-factor Authentication**: SMS/email verification
2. **Social Login**: Google, GitHub integration
3. **User Preferences**: Customizable chat settings
4. **Analytics Dashboard**: User engagement metrics
5. **Admin Panel**: User management interface

### Performance Optimizations
1. **Session Caching**: Redis-based session storage
2. **Connection Pooling**: Optimized database connections
3. **Rate Limiting**: API request throttling
4. **CDN Integration**: Static asset optimization

## ✅ Production Checklist

- [ ] **Environment Variables**: All secrets properly configured
- [ ] **Database**: Production database with proper indexes
- [ ] **SSL/TLS**: HTTPS enabled for all endpoints
- [ ] **Rate Limiting**: API rate limiting implemented
- [ ] **Monitoring**: Application monitoring and logging
- [ ] **Backup**: Database backup strategy in place
- [ ] **Testing**: Authentication flow thoroughly tested

---

**Note**: This authentication system provides a secure, scalable foundation for FeelMate's user management needs. All user data is properly isolated and sessions are managed securely.


