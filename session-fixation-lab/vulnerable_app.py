from flask import Flask, render_template_string, request, session, redirect, url_for, make_response
import uuid
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

USERS = {"testuser": "password123"}

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

app = Flask(__name__)
app.secret_key = 'a_very_insecure_secret_key'

class CustomSession:
    def __init__(self, sid):
        self.sid = sid
        self.logged_in = False
        self.username = None

sessions = {}

@app.before_request
def before_request_func():
    logger.debug(f"Before request: Cookies: {request.cookies}")
    if 'sid' in request.args:
        sid = request.args['sid']
        logger.debug(f"Session ID from URL: {sid}")
        session['sid'] = sid
        if sid not in sessions:
            sessions[sid] = CustomSession(sid)
        session['logged_in'] = sessions[sid].logged_in
        session['username'] = sessions[sid].username
        session.modified = True
        resp = make_response(redirect(request.path))
        resp.set_cookie('custom_session_id', sid)
        return resp
    
    # Prioritize custom_session_id cookie over new UUID
    sid = request.cookies.get('custom_session_id')
    if not sid:
        sid = session.get('sid') or str(uuid.uuid4())
    if sid not in sessions:
        sessions[sid] = CustomSession(sid)
    session['sid'] = sid
    session['logged_in'] = sessions[sid].logged_in
    session['username'] = sessions[sid].username
    session.modified = True
    logger.debug(f"Session data set: sid={sid}, session={session}")

@app.route('/')
def index():
    logger.debug(f"Index route: session.logged_in = {session.get('logged_in')}, session = {session}")
    if session.get('logged_in'):
        return render_template_string(INDEX_HTML)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        logger.debug(f"Login attempt: username={username}, password={password}")
        if USERS.get(username) == password:
            sid = session.get('sid') or str(uuid.uuid4())
            if sid not in sessions:
                sessions[sid] = CustomSession(sid)
            sessions[sid].logged_in = True
            sessions[sid].username = username
            session['sid'] = sid
            session['logged_in'] = True
            session['username'] = username
            session.modified = True
            logger.debug(f"Login successful: sid={sid}, session={session}")
            resp = make_response(redirect(url_for('index')))
            resp.set_cookie('custom_session_id', sid)
            return resp
        else:
            message = "Invalid credentials"
            logger.debug("Login failed: Invalid credentials")
    return render_template_string(LOGIN_HTML, message=message)

@app.route('/logout')
def logout():
    logger.debug(f"Logout: Clearing session for sid={session.get('sid')}")
    sid = session.get('sid')
    if sid in sessions:
        sessions.pop(sid)
    session.clear()
    resp = make_response(redirect(url_for('login')))
    resp.set_cookie('custom_session_id', '', expires=0)
    return resp

if __name__ == '__main__':
    app.run(debug=True)