# Standard Flask imports: core app, templating, request/response handling, and session management
from flask import Flask, render_template_string, request, session, redirect, url_for, make_response
# UUID generation for creating session identifiers
import uuid
# Logging for debugging and tracing application flow
import logging

# Configure logging to output debug-level messages to the console
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Hardcoded user store: in a real app this would be a database
USERS = {"testuser": "password123"}

# HTML template for the login page, styled with Tailwind CSS
LOGIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vulnerable Login</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
        body { font-family: 'Inter', sans-serif; }
    </style>
</head>
<body class="bg-gray-100 flex items-center justify-center min-h-screen">
    <div class="bg-white p-8 rounded-lg shadow-xl w-full max-w-sm">
        <h1 class="text-2xl font-bold mb-6 text-center text-red-600">Vulnerable Login</h1>
        {% if message %}<p class="text-red-500 text-center mb-4">{{ message }}</p>{% endif %}
        <form method="POST">
            <div class="mb-4">
                <label for="username" class="block text-gray-700 font-medium mb-2">Username</label>
                <input type="text" id="username" name="username" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500" required>
            </div>
            <div class="mb-6">
                <label for="password" class="block text-gray-700 font-medium mb-2">Password</label>
                <input type="password" id="password" name="password" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500" required>
            </div>
            <button type="submit" class="w-full bg-red-600 text-white py-2 px-4 rounded-md hover:bg-red-700 transition duration-300 font-semibold">Login</button>
        </form>
    </div>
</body>
</html>
"""

# HTML template for the home page, showing session details and a logout link
INDEX_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vulnerable Home</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
        body { font-family: 'Inter', sans-serif; }
    </style>
</head>
<body class="bg-gray-100 flex items-center justify-center min-h-screen">
    <div class="bg-white p-8 rounded-lg shadow-xl w-full max-w-lg text-center">
        <h1 class="text-3xl font-bold mb-4 text-green-600">Welcome, {{ session['username'] }}!</h1>
        <p class="text-lg text-gray-700 mb-6">Your session ID is currently: <span class="font-mono bg-gray-200 px-2 py-1 rounded-md text-red-600">{{ session.sid }}</span></p>
        <p class="mb-8 text-gray-600">
            **ATTENTION:** This application is intentionally vulnerable to session fixation.
            Notice that the session ID does not change after you log in.
            If an attacker gave you this ID before you logged in, they now have access to your session.
        </p>
        <a href="{{ url_for('logout') }}" class="bg-red-600 text-white py-2 px-4 rounded-md hover:bg-red-700 transition duration-300 font-semibold">Logout</a>
    </div>
</body>
</html>
"""

# Initialize Flask application
app = Flask(__name__)
# Secret key for signing Flask's session cookies (hardcoded insecurely for demonstration)
app.secret_key = 'a_very_insecure_secret_key'

# CustomSession class: represents a server-side session with an ID, authentication state, and username
class CustomSession:
    def __init__(self, sid):
        self.sid = sid          # Unique session identifier
        self.logged_in = False  # Authentication flag
        self.username = None    # Username associated after login

# In-memory store of active CustomSession objects, keyed by sid
sessions = {}

@app.before_request
def before_request_func():
    # Debug log of incoming cookies
    logger.debug(f"Before request: Cookies: {request.cookies}")

    # Check if a session ID was provided via URL parameter (sid)
    if 'sid' in request.args:
        sid = request.args['sid']
        logger.debug(f"Session ID from URL: {sid}")
        # Store the provided sid in Flask's session
        session['sid'] = sid
        # Create a new CustomSession if not existing
        if sid not in sessions:
            sessions[sid] = CustomSession(sid)
        # Sync Flask session flags with our CustomSession
        session['logged_in'] = sessions[sid].logged_in
        session['username'] = sessions[sid].username
        session.modified = True
        # Redirect to the same path and set a cookie for future requests
        resp = make_response(redirect(request.path))
        resp.set_cookie('custom_session_id', sid)
        return resp

    # No URL sid: prefer cookie 'custom_session_id', else fallback to existing Flask session sid or generate new UUID
    sid = request.cookies.get('custom_session_id')
    if not sid:
        sid = session.get('sid') or str(uuid.uuid4())
    # Initialize CustomSession if needed
    if sid not in sessions:
        sessions[sid] = CustomSession(sid)
    # Sync session values
    session['sid'] = sid
    session['logged_in'] = sessions[sid].logged_in
    session['username'] = sessions[sid].username
    session.modified = True
    logger.debug(f"Session data set: sid={sid}, session={session}")

@app.route('/')
def index():
    # Log current login state and session contents
    logger.debug(f"Index route: session.logged_in = {session.get('logged_in')}, session = {session}")
    # If authenticated, render the protected page; otherwise redirect to login
    if session.get('logged_in'):
        return render_template_string(INDEX_HTML)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = None
    # Process login form submission
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        logger.debug(f"Login attempt: username={username}, password={password}")
        # Validate credentials against USERS store
        if USERS.get(username) == password:
            # Reuse existing sid or generate a new one
            sid = session.get('sid') or str(uuid.uuid4())
            if sid not in sessions:
                sessions[sid] = CustomSession(sid)
            # Mark CustomSession as logged in and store username
            sessions[sid].logged_in = True
            sessions[sid].username = username
            # Update Flask session
            session['sid'] = sid
            session['logged_in'] = True
            session['username'] = username
            session.modified = True
            logger.debug(f"Login successful: sid={sid}, session={session}")
            # Redirect to index and set custom session cookie
            resp = make_response(redirect(url_for('index')))
            resp.set_cookie('custom_session_id', sid)
            return resp
        else:
            # Invalid credentials path
            message = "Invalid credentials"
            logger.debug("Login failed: Invalid credentials")
    # Render login page with optional error message
    return render_template_string(LOGIN_HTML, message=message)

@app.route('/logout')
def logout():
    # Log logout event
    logger.debug(f"Logout: Clearing session for sid={session.get('sid')}")
    sid = session.get('sid')
    # Remove server-side CustomSession
    if sid in sessions:
        sessions.pop(sid)
    # Clear Flask session data and expire the cookie
    session.clear()
    resp = make_response(redirect(url_for('login')))
    resp.set_cookie('custom_session_id', '', expires=0)
    return resp

# Entry point: start Flask development server when run directly
if __name__ == '__main__':
    app.run(debug=True)