# Session Fixation Lab

This lab demonstrates the **Session Fixation** vulnerability and its secure implementation. Session fixation is an attack where an attacker can force a user to use a specific session ID, allowing them to hijack the user's session after authentication.

## 🎯 Learning Objectives

- Understand how session fixation attacks work
- Identify vulnerable session management practices
- Learn secure session handling techniques
- Practice exploiting and fixing session fixation vulnerabilities

## 📁 Lab Structure

```plaintext
session_fixation_lab/
├── vulnerable_app.py    # Intentionally vulnerable application
├── patched_app.py       # Secure implementation
├── venv/               # Python virtual environment
└── README.md           # This file
```

## 🚨 The Vulnerability

### What is Session Fixation?

Session fixation occurs when an application accepts a session identifier from the client (typically via URL parameter) and doesn't regenerate it after authentication. This allows attackers to:

1. **Pre-generate** a session ID
2. **Force** a user to use that session ID (via URL manipulation)
3. **Hijack** the session after the user logs in

### Vulnerable Implementation

The `vulnerable_app.py` demonstrates these insecure practices:

- ✅ Accepts session IDs from URL parameters
- ✅ Doesn't regenerate session ID after login
- ✅ Stores session data in memory without proper validation
- ✅ No session timeout or security headers

## 🛠️ Setup Instructions

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Installation

1. **Navigate to the lab directory:**

   ```bash
   cd session_fixation_lab
   ```

2. **Create and activate virtual environment:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install flask
   ```

## 🧪 Running the Lab

### Step 1: Start the Vulnerable Application

```bash
python vulnerable_app.py
```

The application will be available at `http://localhost:5000`

### Step 2: Demonstrate the Attack

1. **Generate a session ID:**
   - Visit `http://localhost:5000/?sid=ATTACKER_SESSION_ID`
   - Notice the session ID is set to `ATTACKER_SESSION_ID`

2. **Login as a user:**
   - Go to `http://localhost:5000/login`
   - Login with credentials: `testuser` / `password123`
   - **Observe:** The session ID remains `ATTACKER_SESSION_ID`

3. **Session hijacking:**
   - An attacker can now access the session using the known session ID
   - Visit `http://localhost:5000/?sid=ATTACKER_SESSION_ID` to see the authenticated session

### Step 3: Test the Secure Implementation

1. **Stop the vulnerable app** (Ctrl+C)

2. **Start the patched application:**

   ```bash
   python patched_app.py
   ```

3. **Test the secure version:**
   - Try the same attack steps above
   - **Notice:** The application ignores attacker-provided session IDs
   - Session IDs are regenerated after login
   - Additional security measures are in place

## 🔒 Security Fixes in Patched Version

### 1. Session ID Regeneration

```python
# Regenerate session ID to prevent session fixation
old_sid = session.get('sid')
if old_sid in sessions:
    sessions.pop(old_sid)  # Remove old session
sid = str(uuid.uuid4())  # Generate new session ID
```

### 2. Ignore Attacker-Provided Session IDs

```python
# Ignore attacker-provided sid to prevent session fixation
if 'sid' in request.args:
    logger.debug("Ignoring attacker-provided sid to prevent session fixation")
    return redirect(request.path)
```

### 3. User-Agent Binding

```python
user_agent_hash = hashlib.sha256(user_agent.encode('utf-8')).hexdigest()
# Validate User-Agent to prevent session hijacking
if sessions[sid].user_agent_hash != user_agent_hash:
    # Invalidate session
```

### 4. Session Timeout

```python
SESSION_TIMEOUT = 900  # 15 minutes
if time.time() - sessions[sid].created_at > SESSION_TIMEOUT:
    # Session expired
```

### 5. Secure Cookie Configuration

```python
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Mitigate CSRF attacks
```

## 🎓 Key Takeaways

### Vulnerable Patterns to Avoid

- ❌ Accepting session IDs from URL parameters
- ❌ Not regenerating session IDs after authentication
- ❌ No session timeout or validation
- ❌ Weak cookie security settings

### Secure Practices

- ✅ Always regenerate session IDs after login
- ✅ Ignore client-provided session identifiers
- ✅ Implement session timeouts
- ✅ Bind sessions to User-Agent or other client characteristics
- ✅ Use secure cookie attributes (HttpOnly, SameSite, Secure)
- ✅ Implement proper session validation

## 🔍 Additional Resources

- [OWASP Session Fixation](https://owasp.org/www-community/attacks/Session_fixation)
- [OWASP Session Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)
- [Flask Session Security](https://flask.palletsprojects.com/en/2.3.x/security/)

## ⚠️ Disclaimer

This lab is for educational purposes only. The vulnerable application is intentionally insecure and should never be used in production environments.

---

### Happy SFA Learning! 🔐🚀
