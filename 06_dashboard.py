import os
import json
import sqlite3
import time
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, g

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_soc'

DATABASE = 'auth.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        db.commit()

# --- AUTH ROUTES ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        cursor = get_db().cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        
        if user and check_password_hash(user[2], password):
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Invalid Credentials")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        db = get_db()
        cursor = db.cursor()
        
        try:
            hashed_pw = generate_password_hash(password)
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_pw))
            db.commit()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return render_template('register.html', error="Username already exists")
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- DASHBOARD ROUTES ---
@app.route('/')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('index.html', username=session['username'])

# --- DUAL MODE API ---
# MODE 1: LIVE STREAM
@app.route('/api/logs/live')
def get_live_logs():
    if not session.get('logged_in'):
        return jsonify([])
        
    logs_dir = "data/processed_logs"
    if not os.path.exists(logs_dir):
        return jsonify([])
        
    files = sorted([f for f in os.listdir(logs_dir) if f.endswith('.json')])
    if not files:
        return jsonify([])
        
    latest_file = os.path.join(logs_dir, files[-1])
    try:
        data = []
        with open(latest_file, 'r') as f:
            for line in f:
                if line.strip():
                    data.append(json.loads(line))
        return jsonify(data)
    except Exception as e:
        return jsonify([])

# MODE 2: DATASET STREAM (Simulating historical big data)
dataset_cursor = 0
@app.route('/api/logs/dataset')
def get_dataset_logs():
    if not session.get('logged_in'):
        return jsonify([])
    
    global dataset_cursor
    historical_file = "data/historical_website.log"
    
    # We will grab 50 logs at a time to simulate high-velocity data processing
    data = []
    
    if not os.path.exists(historical_file):
        return jsonify([])
        
    try:
        with open(historical_file, 'r') as f:
            # Skip to the current cursor position
            for _ in range(dataset_cursor):
                f.readline()
            
            # Read the next 50 logs
            for _ in range(50):
                line = f.readline()
                if not line:
                    # Loop back to start if we reach the end
                    dataset_cursor = 0
                    break
                
                # Mock anomaly generation in historical data for the dashboard to find
                flag = "NORMAL"
                if dataset_cursor % 500 == 0:
                    flag = "CRITICAL: Historical Database Breach"
                elif dataset_cursor % 100 == 0:
                    flag = "HIGH: Automated Scraper"
                    
                data.append({
                    "processing_time": datetime.now().isoformat() if 'datetime' in globals() else str(time.time()),
                    "raw_log": line.strip(),
                    "alert_flag": flag,
                    "ml_cluster": 0
                })
                dataset_cursor += 1
                
        return jsonify(data)
    except Exception as e:
        return jsonify([])

if __name__ == '__main__':
    from datetime import datetime
    init_db()
    print("Starting Enterprise SOC Dashboard on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
