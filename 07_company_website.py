import os
import random
import logging
from flask import Flask, render_template_string, request

app = Flask(__name__)

# Disable default werkzeug logger interference
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Set up our custom isolated logger
custom_logger = logging.getLogger('SOC_Logger')
custom_logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('data/live_website.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
custom_logger.addHandler(file_handler)

# STUNNING E-COMMERCE WEBSITE WITH BOOTSTRAP 5
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NexGen Store | Premium Electronics</title>
    <!-- Bootstrap 5 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f8f9fa; }
        .navbar-brand { font-weight: 800; font-size: 24px; color: #0d6efd !important; }
        .hero-section {
            background: linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.6)), url('https://images.unsplash.com/photo-1550745165-9bc0b252726f?auto=format&fit=crop&w=1200&q=80') center/cover;
            color: white; padding: 100px 0; text-align: center;
        }
        .hero-section h1 { font-size: 3.5rem; font-weight: 700; margin-bottom: 20px; }
        .product-card { transition: transform 0.3s; border: none; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .product-card:hover { transform: translateY(-5px); }
        .footer { background: #212529; color: #adb5bd; padding: 40px 0; margin-top: 50px; }
        
        /* Hacker Terminal - Permanently Visible Tab */
        #hackerTerminal {
            position: fixed; bottom: -600px; right: 20px; width: 450px; background: #000;
            border: 2px solid #0f0; border-radius: 8px 8px 0 0; color: #0f0; font-family: monospace;
            transition: bottom 0.4s ease; z-index: 1050; box-shadow: 0 0 20px rgba(0, 255, 0, 0.4);
        }
        #hackerTerminal.active { bottom: 0; }
        .terminal-header { background: #111; padding: 15px; border-bottom: 2px solid #0f0; display: flex; justify-content: space-between; align-items: center; cursor: pointer; border-radius: 8px 8px 0 0; font-weight: bold; font-size: 16px;}
        .terminal-body { padding: 15px; height: 450px; overflow-y: auto; }
        .btn-hack { width: 100%; margin-bottom: 12px; background: #111; color: #0f0; border: 1px solid #0f0; text-align: left; padding: 10px; transition: all 0.2s; border-radius: 4px; }
        .btn-hack:hover { background: #0f0; color: #000; font-weight: bold; }
        .btn-hack span { display: block; font-size: 11px; opacity: 0.8; margin-top: 4px; }
        
        #devTrigger { 
            position: fixed; bottom: 20px; right: 20px; background: #000; color: #0f0; border: 2px solid #0f0; 
            padding: 10px 20px; font-weight: bold; font-family: monospace; cursor: pointer; z-index: 1060; border-radius: 4px;
            box-shadow: 0 0 10px rgba(0,255,0,0.5); transition: 0.3s;
        }
        #devTrigger:hover { background: #0f0; color: #000; }
        
        #toastContainer { position: fixed; top: 20px; right: 20px; z-index: 1060; }
    </style>
</head>
<body>
    <!-- Navbar -->
    <nav class="navbar navbar-expand-lg navbar-light bg-white shadow-sm sticky-top">
        <div class="container">
            <a class="navbar-brand" href="#" onclick="sendReq('/home')"><i class="bi bi-cpu"></i> NexGen Store</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item"><a class="nav-link" href="#" onclick="sendReq('/products')">Products</a></li>
                    <li class="nav-item"><a class="nav-link" href="#" onclick="sendReq('/categories')">Categories</a></li>
                    <li class="nav-item"><a class="nav-link" href="#" onclick="sendReq('/cart')"><i class="bi bi-cart"></i> Cart (0)</a></li>
                    <li class="nav-item ms-2"><button class="btn btn-primary" onclick="sendReq('/login')">Sign In</button></li>
                </ul>
            </div>
        </div>
    </nav>

    <!-- Hero -->
    <div class="hero-section">
        <div class="container">
            <h1>The Future of Computing</h1>
            <p class="lead">Experience unprecedented performance with our latest lineup.</p>
            <button class="btn btn-primary btn-lg mt-3" onclick="sendReq('/shop-now')">Shop Now</button>
        </div>
    </div>

    <!-- Products -->
    <div class="container mt-5">
        <h2 class="text-center mb-4">Featured Products</h2>
        <div class="row">
            <div class="col-md-4 mb-4">
                <div class="card product-card">
                    <img src="https://images.unsplash.com/photo-1496181133206-80ce9b88a853?auto=format&fit=crop&w=500&q=60" class="card-img-top" alt="Laptop">
                    <div class="card-body text-center">
                        <h5 class="card-title">NexBook Pro</h5>
                        <p class="card-text text-primary fw-bold">$1,299</p>
                        <button class="btn btn-outline-dark w-100" onclick="sendReq('/add-to-cart/1')">Add to Cart</button>
                    </div>
                </div>
            </div>
            <div class="col-md-4 mb-4">
                <div class="card product-card">
                    <img src="https://images.unsplash.com/photo-1546868871-7041f2a55e12?auto=format&fit=crop&w=500&q=60" class="card-img-top" alt="Watch">
                    <div class="card-body text-center">
                        <h5 class="card-title">NexWatch Series 5</h5>
                        <p class="card-text text-primary fw-bold">$399</p>
                        <button class="btn btn-outline-dark w-100" onclick="sendReq('/add-to-cart/2')">Add to Cart</button>
                    </div>
                </div>
            </div>
            <div class="col-md-4 mb-4">
                <div class="card product-card">
                    <img src="https://images.unsplash.com/photo-1583394838336-acd977736f90?auto=format&fit=crop&w=500&q=60" class="card-img-top" alt="Headphones">
                    <div class="card-body text-center">
                        <h5 class="card-title">NexPods Max</h5>
                        <p class="card-text text-primary fw-bold">$249</p>
                        <button class="btn btn-outline-dark w-100" onclick="sendReq('/add-to-cart/3')">Add to Cart</button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Footer -->
    <footer class="footer">
        <div class="container text-center">
            <p>&copy; 2026 NexGen Store. All rights reserved.</p>
        </div>
    </footer>

    <!-- Secret Invisible Button to Trigger Terminal -->
    <div id="devTrigger" onclick="document.getElementById('hackerTerminal').classList.toggle('active'); this.style.display='none';">Launch Attack Simulator</div>

    <!-- Hacker Terminal -->
    <div id="hackerTerminal">
        <div class="terminal-header" onclick="document.getElementById('hackerTerminal').classList.remove('active'); document.getElementById('devTrigger').style.display='block';">
            <span>root@kali:~# Attack Vectors</span>
            <span>▼ Minimize</span>
        </div>
        <div class="terminal-body">
            <button class="btn-hack" onclick="sendReq('/attack/sqli')">
                [1] SQL Injection 
                <span>Attempts to bypass login auth via SQL map dump payloads.</span>
            </button>
            <button class="btn-hack" onclick="sendReq('/attack/bruteforce')">
                [2] Credential Brute Force
                <span>Rapid SSH/HTTP login attempts with Hydra dictionary attack.</span>
            </button>
            <button class="btn-hack" onclick="sendReq('/attack/traversal')">
                [3] Path Traversal
                <span>Tries to read sensitive local files like /etc/passwd via URL manipulation.</span>
            </button>
            <button class="btn-hack" onclick="sendReq('/attack/ddos')">
                [4] DDoS Flood
                <span>Simulates high-volume traffic causing Rate Limit exceptions.</span>
            </button>
            <button class="btn-hack" onclick="sendReq('/attack/xss')">
                [5] Cross-Site Scripting (XSS)
                <span>Injects malicious javascript payloads into form fields.</span>
            </button>
            <button class="btn-hack" onclick="sendReq('/attack/500')">
                [6] Service Crash Injection
                <span>Forces a NullPointerException in the backend gateway.</span>
            </button>
            <button class="btn-hack" onclick="sendReq('/attack/privesc')">
                [7] Privilege Escalation
                <span>Manipulates PUT request payloads to steal admin roles.</span>
            </button>
            <button class="btn-hack" onclick="sendReq('/attack/csrf')">
                [8] CSRF Forgery
                <span>Attempts to bypass Cross-Site Request Forgery tokens.</span>
            </button>
        </div>
    </div>

    <!-- Toast Notifications -->
    <div id="toastContainer"></div>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function sendReq(endpoint) {
            fetch(endpoint)
                .then(res => res.text())
                .then(data => {
                    const isAttack = endpoint.includes('attack');
                    showToast(data, isAttack);
                });
        }

        function showToast(message, isAttack) {
            const toastId = 'toast' + Date.now();
            const bgClass = isAttack ? 'bg-danger text-white' : 'bg-primary text-white';
            const icon = isAttack ? '<i class="bi bi-shield-x me-2"></i>' : '<i class="bi bi-info-circle me-2"></i>';
            
            const toastHTML = `
                <div id="${toastId}" class="toast align-items-center ${bgClass} border-0 mb-2" role="alert" aria-live="assertive" aria-atomic="true">
                    <div class="d-flex">
                        <div class="toast-body fw-bold">
                            ${icon} ${message}
                        </div>
                        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                    </div>
                </div>
            `;
            
            document.getElementById('toastContainer').insertAdjacentHTML('beforeend', toastHTML);
            const toastElement = document.getElementById(toastId);
            const toast = new bootstrap.Toast(toastElement, { delay: 2000 });
            toast.show();
            
            toastElement.addEventListener('hidden.bs.toast', () => {
                toastElement.remove();
            });
        }
    </script>
</body>
</html>
"""

from kafka import KafkaProducer
import json

# Setup Kafka Producer
try:
    kafka_producer = KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    print("Successfully connected to Kafka Broker!")
except Exception as e:
    print(f"Warning: Kafka not running or reachable. Logs will only go to file. Error: {e}")
    kafka_producer = None

def log_event(level, msg):
    ip = request.remote_addr or "192.168.1.100"
    full_msg = f"{ip} {msg}"
    custom_logger.log(level, full_msg)
    
    # Stream to Kafka
    if kafka_producer:
        try:
            kafka_producer.send('soc_logs', {'log': full_msg})
            kafka_producer.flush()
        except Exception:
            pass
            
    return "Event sent to server logs and Kafka stream."

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/<path:page>")
def normal_page(page):
    # Silently ignore browser background requests & attack routes (handled by dedicated routes)
    if page == 'favicon.ico' or page.startswith('attack/') or page == 'attack':
        return "", 204
    # Log genuine user navigation as NORMAL traffic
    latency = random.randint(10, 150)
    log_event(logging.INFO, f"USER=guest REQ=GET /{page} STATUS=200 LATENCY={latency}ms")
    return f"Loaded /{page} successfully"

# --- 8 CYBER ATTACK ROUTES ---
@app.route("/attack/sqli")
def attack_sqli():
    return log_event(logging.ERROR, "REQ=POST /login PAYLOAD='admin\\' OR 1=1; UNION SELECT * FROM users--' ERROR=SQLSyntaxError")

@app.route("/attack/bruteforce")
def attack_brute():
    return log_event(logging.WARNING, "REQ=POST /login USER=admin STATUS=401 MSG='Login failed (Attempt 145)'")

@app.route("/attack/traversal")
def attack_traversal():
    return log_event(logging.CRITICAL, "REQ=GET /download?file=../../../../etc/passwd STATUS=403")

@app.route("/attack/ddos")
def attack_ddos():
    return log_event(logging.WARNING, "REQ=GET /api/data STATUS=429 MSG='Rate Limit Exceeded (1000 req/sec)'")

@app.route("/attack/xss")
def attack_xss():
    return log_event(logging.WARNING, "REQ=POST /comment PAYLOAD='<script>alert(document.cookie)</script>' STATUS=400")

@app.route("/attack/500")
def attack_500():
    return log_event(logging.CRITICAL, "REQ=GET /checkout STATUS=500 MSG='Internal Server Error: NullPointerException in PaymentGateway'")

@app.route("/attack/privesc")
def attack_privesc():
    return log_event(logging.CRITICAL, "REQ=PUT /api/users/12 PAYLOAD='{\"role\":\"admin\"}' STATUS=200 MSG='Unauthorized Role Modification'")

@app.route("/attack/csrf")
def attack_csrf():
    return log_event(logging.WARNING, "REQ=POST /account/transfer STATUS=403 MSG='Invalid or Missing CSRF Token'")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False)
