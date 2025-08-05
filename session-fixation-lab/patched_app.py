from flask import Flask, render_template_string, request, session, redirect, url_for, make_response
import uuid
import hashlib
import logging
import time

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# A hardcoded user for this demonstration
USERS = {"testuser": "password123"}

# Session timeout in seconds (e.g., 15 minutes)
SESSION_TIMEOUT = 900

# The HTML for the login page
LOGIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Secure Login</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
        body { font-family: 'Inter', sans-serif; }
    </style>
</head>
<body class="bg-gray-100 flex items-center justify-center min-h-screen">
    <div class="bg-white p-8 rounded-lg shadow-xl w-full max-w-sm">
        <h1 class="text-2xl font-bold mb-6 text-center text-blue-600">Secure Login</h1>
        {% if message %}<p class="text-red-500 text-center mb-4">{{ message }}</p>{% endif %}
        <form method="POST">
            <div class="mb-4">
                <label for="username" class="block text-gray-700 font-medium mb-2">Username</label>
                <input type="text" id="username" name="username" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" required>
            </div>
            <div class="mb-6">
                <label for="password" class="block text-gray-700 font-medium mb-2">Password</label>
                <input type="password" id="password" name="password" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" required>
            </div>
            <button type="submit" class="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition duration-300 font-semibold">Login</button>
        </form>
    </div>
</body>
</html>
"""

# The HTML for the dashboard page
INDEX_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Secure Home</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
        body { font-family: 'Inter', sans-serif; }
    </style>
</head>
<body class="bg-gray-100 flex items-center justify-center min-h-screen">
    <div class="bg-white p-8 rounded-lg shadow-xl w-full max-w-lg text-center">
        <h1 class="text-3xl font-bold mb-4 text-green-600">Welcome, {{ session['username'] }}!</h1>
        <p class="mb-8 text-gray-600">
            This application is secure against session fixation and session hijacking.
            The session ID is regenerated upon login, sessions are bound to your browser's User-Agent,
            and a unique session token prevents cookie reuse across browser contexts.
        </p>
        <a href="{{ url_for('logout') }}" class="bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition duration-300 font-semibold">Logout</a>
    </div>
</body>
</html>
"""

app = Flask(__name__)
app.secret_key = 'a_secure_random_secret_key'  # Use a secure random key in production
app.config['SESSION_COOKIE_SECURE'] = False  # Set to False for local testing without HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access to cookie
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Mitigate CSRF attacks

# A simple dictionary to store custom sessions
sessions = {}

# A custom session class
class CustomSession:
    def __init__(self, sid, user_agent_hash, session_token, created_at):
        self.sid = sid
        self.user_agent_hash = user_agent_hash
        self.session_token = session_token
        self.created_at = created_at
        self.logged_in = False
        self.username = None

# Middleware to handle session logic
@app.before_request
def before_request_func():
    logger.debug(f"Before request: Cookies: {request.cookies}")
    # Ignore attacker-provided sid to prevent session fixation
    if 'sid' in request.args:
        logger.debug("Ignoring attacker-provided sid to prevent session fixation")
        return redirect(request.path)
    
    # Get current User-Agent hash and session token
    user_agent = request.headers.get('User-Agent', '')
    user_agent_hash = hashlib.sha256(user_agent.encode('utf-8')).hexdigest()
    current_session_token = session.get('session_token')
    
    # Use the session ID from the Flask session or cookie if available
    sid = session.get('sid') or request.cookies.get('custom_session_id')
    if not sid or sid not in sessions:
        sid = str(uuid.uuid4())
        session_token = str(uuid.uuid4())
        sessions[sid] = CustomSession(sid, user_agent_hash, session_token, time.time())
        session['sid'] = sid
        session['session_token'] = session_token
        logger.debug(f"Created new session ID: {sid} with user_agent_hash: {user_agent_hash}, session_token: {session_token}")
        # Do not return here; let the route handle the response
    else:
        # Validate User-Agent and session token
        if (sessions[sid].user_agent_hash != user_agent_hash or
            sessions[sid].session_token != current_session_token):
            logger.debug(f"Validation failed: User-Agent stored={sessions[sid].user_agent_hash}, current={user_agent_hash}; "
                         f"Session token stored={sessions[sid].session_token}, current={current_session_token}")
            sessions.pop(sid, None)
            session.clear()
            resp = make_response(redirect(url_for('login')))
            resp.set_cookie('custom_session_id', '', expires=0, secure=app.config['SESSION_COOKIE_SECURE'], httponly=True, samesite='Lax')
            return resp
        
        # Check session timeout
        if time.time() - sessions[sid].created_at > SESSION_TIMEOUT:
            logger.debug(f"Session expired: sid={sid}")
            sessions.pop(sid, None)
            session.clear()
            resp = make_response(redirect(url_for('login')))
            resp.set_cookie('custom_session_id', '', expires=0, secure=app.config['SESSION_COOKIE_SECURE'], httponly=True, samesite='Lax')
            return resp
    
    # Synchronize Flask session with custom session
    session['logged_in'] = sessions[sid].logged_in
    session['username'] = sessions[sid].username
    session.modified = True
    logger.debug(f"Session data set: {session}")

@app.route('/')
def index():
    logger.debug(f"Index route: session.logged_in = {session.get('logged_in')}, session = {session}")
    if session.get('logged_in'):
        resp = make_response(render_template_string(INDEX_HTML))
    else:
        resp = make_response(redirect(url_for('login')))
    # Set custom_session_id cookie
    resp.set_cookie('custom_session_id', session['sid'], secure=app.config['SESSION_COOKIE_SECURE'], httponly=True, samesite='Lax')
    return resp

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Redirect to index if already logged in
    if session.get('logged_in'):
        logger.debug(f"Already logged in, redirecting to index: session={session}")
        resp = make_response(redirect(url_for('index')))
        resp.set_cookie('custom_session_id', session['sid'], secure=app.config['SESSION_COOKIE_SECURE'], httponly=True, samesite='Lax')
        return resp
    
    message = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        logger.debug(f"Login attempt: username={username}, password={password}")
        if USERS.get(username) == password:
            # Get current User-Agent hash and session token
            user_agent = request.headers.get('User-Agent', '')
            user_agent_hash = hashlib.sha256(user_agent.encode('utf-8')).hexdigest()
            session_token = str(uuid.uuid4())
            
            # Regenerate session ID to prevent session fixation
            old_sid = session.get('sid')
            if old_sid in sessions:
                sessions.pop(old_sid)  # Remove old session
            sid = str(uuid.uuid4())  # Generate new session ID
            sessions[sid] = CustomSession(sid, user_agent_hash, session_token, time.time())
            session.clear()  # Clear existing session data
            session['sid'] = sid
            session['session_token'] = session_token
            sessions[sid].logged_in = True
            sessions[sid].username = username
            session['logged_in'] = True
            session['username'] = username
            session.modified = True
            logger.debug(f"Login successful: new sid={sid}, user_agent_hash={user_agent_hash}, session_token={session_token}, session={session}")
            resp = make_response(redirect(url_for('index')))
            resp.set_cookie('custom_session_id', sid, secure=app.config['SESSION_COOKIE_SECURE'], httponly=True, samesite='Lax')
            return resp
        else:
            message = "Invalid credentials"
            logger.debug("Login failed: Invalid credentials")
    resp = make_response(render_template_string(LOGIN_HTML, message=message))
    resp.set_cookie('custom_session_id', session['sid'], secure=app.config['SESSION_COOKIE_SECURE'], httponly=True, samesite='Lax')
    return resp

@app.route('/logout')
def logout():
    logger.debug(f"Logout: Clearing session for sid={session.get('sid')}")
    # Clear the session data and redirect to login
    sid = session.get('sid')
    if sid in sessions:
        sessions.pop(sid)
    session.clear()
    resp = make_response(redirect(url_for('login')))
    resp.set_cookie('custom_session_id', '', expires=0, secure=app.config['SESSION_COOKIE_SECURE'], httponly=True, samesite='Lax')
    return resp

if __name__ == '__main__':
    app.run(debug=True)