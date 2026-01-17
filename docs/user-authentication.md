# User Authentication Workflow

## Overview

Authentication is handled via Google OAuth 2.0. Users log in with their Google account, and the backend creates a session stored in Flask's session management.

## Architecture

```
Frontend → Google OAuth → Backend Session → Database User Record
```

## Endpoints

### 1. Initiate Google Login

**Endpoint**: `GET /login/google`

**Purpose**: Redirects user to Google OAuth consent screen

**Controller**: `usersController.py:15`

**Flow**:
1. Frontend redirects to this endpoint
2. Backend generates OAuth redirect URL
3. User is sent to Google login page

**Code Reference**:
```python
# File: app/controllers/usersController.py:15
@usersController.route('/login/google')
def login():
    redirect_uri = url_for('usersController.authorize', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)
```

**Request Example**:
```http
GET /login/google HTTP/1.1
Host: localhost:5000
```

**Response**: HTTP 302 Redirect to Google OAuth

---

### 2. Google OAuth Callback

**Endpoint**: `GET /authorize/google`

**Purpose**: Receives OAuth callback from Google and establishes session

**Controller**: `usersController.py:20`

**Service**: `userService.py:39` (`login_or_create_user`)

**Flow**:
1. Google redirects back with authorization code
2. Backend exchanges code for access token
3. Fetches user info from Google
4. Creates or retrieves User record
5. Stores username in Flask session
6. Redirects to frontend

**Code Reference**:
```python
# File: app/controllers/usersController.py:20-36
@usersController.route('/authorize/google')
def authorize():
    token = oauth.google.authorize_access_token()
    user_info = token.get('userinfo')

    if user_info:
        username = user_info['email']
        result = UserService.login_or_create_user(username)
        session['username'] = username

        return redirect(f"{frontend_url}")
```

**Service Logic**:
```python
# File: app/services/userService.py:39-60
@staticmethod
def login_or_create_user(username):
    existing_user = User.query.filter_by(username=username).first()

    if existing_user:
        return {"message": "User logged in successfully."}
    else:
        new_user = User(username=username)
        db.session.add(new_user)
        db.session.commit()
        return {"message": "User created and logged in successfully."}
```

**Request Example**:
```http
GET /authorize/google?code=4/0Abc123...&state=xyz HTTP/1.1
Host: localhost:5000
```

**Response**: HTTP 302 Redirect to frontend with session cookie

**Session Data Stored**:
```python
{
    "username": "user@gmail.com"
}
```

---

### 3. Check Login Status

**Endpoint**: `GET /check_logged_in`

**Purpose**: Verify if user has active session

**Controller**: `usersController.py:51`

**Flow**:
1. Frontend checks if user is logged in
2. Backend checks for username in session
3. Returns username if logged in, error if not

**Code Reference**:
```python
# File: app/controllers/usersController.py:51-65
@usersController.route('/check_logged_in', methods=['GET'])
def check_logged_in():
    username = session.get('username')

    if username:
        return jsonify({"username": username}), 200
    else:
        return jsonify({"error": "User not logged in"}), 401
```

**Request Example**:
```http
GET /check_logged_in HTTP/1.1
Host: localhost:5000
Cookie: session=eyJ1c2VybmFtZSI6InVzZXJAZ21haWwuY29tIn0...
```

**Success Response** (200):
```json
{
  "username": "user@gmail.com"
}
```

**Error Response** (401):
```json
{
  "error": "User not logged in"
}
```

---

### 4. Check Session Info

**Endpoint**: `GET /session-info`

**Purpose**: Retrieve current session information including auth provider

**Controller**: `usersController.py:79`

**Flow**:
1. Frontend checks session status
2. Backend returns username and auth provider if logged in
3. Returns 401 error if no active session

**Code Reference**:
```python
# File: app/controllers/usersController.py:79-95
@usersController.route('/session-info', methods=['GET'])
def session_info():
    if 'username' in session:
        return jsonify({
            'username': session['username'],
            'auth_provider': session.get('auth_provider', 'local')
        })
    return jsonify({'error': 'Not logged in'}), 401
```

**Request Example**:
```http
GET /session-info HTTP/1.1
Host: localhost:5000
Cookie: session=eyJ1c2VybmFtZSI6InVzZXJAZ21haWwuY29tIn0...
```

**Success Response** (200):
```json
{
  "username": "user@gmail.com",
  "auth_provider": "google"
}
```

**Error Response** (401):
```json
{
  "error": "Not logged in"
}
```

---

### 5. Logout

**Endpoint**: `POST /logout`

**Purpose**: Clear user session and log out

**Controller**: `usersController.py:97`

**Flow**:
1. Frontend calls logout endpoint
2. Backend clears session using `session.clear()`
3. Returns success message

**Code Reference**:
```python
# File: app/controllers/usersController.py:97-108
@usersController.route('/logout', methods=['POST'])
def logout():
    username = session.get('username', 'Unknown')
    session.clear()
    logging.info(f"User {username} logged out successfully")
    return jsonify({'message': 'Logged out successfully'}), 200
```

**Request Example**:
```http
POST /logout HTTP/1.1
Host: localhost:5000
Content-Type: application/json
Cookie: session=eyJ1c2VybmFtZSI6InVzZXJAZ21haWwuY29tIn0...
```

**Success Response** (200):
```json
{
  "message": "Logged out successfully"
}
```

---

## Database Schema

### User Model

**File**: `app/models/userModel.py`

```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True, nullable=False)

    # Relationship to players in different leagues
    players = db.relationship('Player', backref='user', lazy=True)
```

**Fields**:
- `id` (Integer, PK): Auto-incrementing unique identifier
- `username` (String, Unique): Email from Google (e.g., "user@gmail.com")

**Relationships**:
- `players`: One-to-many with Player model (user can be in multiple leagues)

---

## Configuration

### OAuth Setup

**File**: `app/__init__.py:47-53`

```python
oauth = OAuth(app)
oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)
```

**Environment Variables Required**:
- `GOOGLE_CLIENT_ID`: Google OAuth client ID
- `GOOGLE_CLIENT_SECRET`: Google OAuth client secret
- `FRONTEND_URL`: Frontend URL for redirects (default: http://localhost:3000)

### Session Configuration

**File**: `app/__init__.py:33-36`

```python
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
```

---

## Frontend Integration

### Login Flow

```javascript
// Redirect to backend login endpoint
window.location.href = 'http://localhost:5000/login/google';

// After OAuth, user is redirected back to frontend
// Check login status
const response = await fetch('http://localhost:5000/check_logged_in', {
  method: 'GET',
  credentials: 'include'  // IMPORTANT: Include session cookie
});

if (response.ok) {
  const data = await response.json();
  console.log('Logged in as:', data.username);
}
```

### Logout Flow

```javascript
// Call logout endpoint to clear session
await fetch('http://localhost:5000/logout', {
  method: 'POST',
  credentials: 'include',  // Include session cookie
  headers: {
    'Content-Type': 'application/json'
  }
});

// Clear local storage
localStorage.removeItem('username');
localStorage.removeItem('auth_provider');
localStorage.setItem('authorized', 'false');

// Redirect to login page
navigate('/login');
```

### Making Authenticated Requests

**IMPORTANT**: All authenticated endpoints require `credentials: 'include'`:

```javascript
const response = await fetch('http://localhost:5000/get_users_leagues?username=user@gmail.com', {
  method: 'GET',
  credentials: 'include',  // Include session cookie
  headers: {
    'Content-Type': 'application/json'
  }
});
```

---

## Common Errors

### 1. CORS Issues

**Error**: `Access-Control-Allow-Origin` header missing

**Cause**: CORS not configured or credentials not included

**Solution**:
- Backend: Ensure CORS allows credentials (`supports_credentials=True`)
- Frontend: Include `credentials: 'include'` in all fetch requests

**Code Reference**: `app/__init__.py:38-42`
```python
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000"],
        "supports_credentials": True
    }
})
```

---

### 2. Session Not Persisting

**Error**: User logged in but `/check_logged_in` returns 401

**Cause**: Session cookie not being sent/stored

**Solution**:
- Check `credentials: 'include'` is set in frontend
- Verify `SESSION_COOKIE_SAMESITE` is 'Lax' or 'None'
- Check browser isn't blocking third-party cookies

---

### 3. OAuth Error: access_denied

**Error**: Google OAuth returns `error=access_denied`

**Cause**: User denied consent or OAuth credentials invalid

**Solution**:
- Verify `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are correct
- Check OAuth redirect URI is whitelisted in Google Console
- Ensure user grants permissions on consent screen

---

### 4. User Not Found After Login

**Error**: Session exists but user record missing from database

**Cause**: Database creation failed or user was deleted

**Solution**:
- Check database logs for errors
- Verify `UserService.login_or_create_user()` completes successfully
- Check for unique constraint violations on username

---

## Security Considerations

1. **HTTPS in Production**: Set `SESSION_COOKIE_SECURE = True` when using HTTPS
2. **Secret Key**: Use strong `SECRET_KEY` for session encryption
3. **CSRF Protection**: Consider adding CSRF tokens for state-changing operations
4. **Session Expiration**: Configure `PERMANENT_SESSION_LIFETIME` for auto-logout
5. **OAuth Scopes**: Only request necessary scopes ('openid email profile')

---

## Testing

### Manual Testing

1. Navigate to `/login/google`
2. Complete Google OAuth flow
3. Verify redirect to frontend
4. Check `/check_logged_in` returns username
5. Navigate to `/logout`
6. Verify `/check_logged_in` returns 401

### Automated Testing

See `tests/test_authentication.py` (if exists) for integration tests.

---

## Related Workflows

- [User Registration](./user-registration.md) - First-time user setup
- [League Join](./league-join.md) - Requires authentication

---

*Last Updated: January 2026*
