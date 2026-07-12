import csv
import random
import os

os.makedirs("data", exist_ok=True)

def generate_labeled_data():
    endpoints = ['/home', '/products', '/about', '/contact', '/checkout', '/login', '/api/data']
    
    anomalies = [
        {"endpoint": "/login", "payload": "admin' OR 1=1; UNION SELECT * FROM users--", "label": "CRITICAL: SQL Injection"},
        {"endpoint": "/login", "payload": "Login failed (Attempt 45)", "label": "HIGH: Brute Force Attack"},
        {"endpoint": "/download?file=../../../../etc/passwd", "payload": "", "label": "CRITICAL: Path Traversal Attempt"},
        {"endpoint": "/api/data", "payload": "Rate Limit Exceeded", "label": "HIGH: DDoS / Rate Limit"},
        {"endpoint": "/comment", "payload": "<script>alert(1)</script>", "label": "MEDIUM: XSS Payload Detected"},
        {"endpoint": "/checkout", "payload": "NullPointerException", "label": "CRITICAL: Application Crash"},
        {"endpoint": "/api/users/12", "payload": "Unauthorized Role Modification", "label": "HIGH: Privilege Escalation"},
        {"endpoint": "/account/transfer", "payload": "Invalid or Missing CSRF Token", "label": "LOW: CSRF Token Bypass"}
    ]

    with open("data/training_data.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["log_text", "label"])
        
        # Generate 5000 normal logs
        for _ in range(5000):
            ip = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
            endpoint = random.choice(endpoints)
            log = f"{ip} USER=guest REQ=GET {endpoint} STATUS=200 LATENCY={random.randint(10, 150)}ms"
            writer.writerow([log, "NORMAL"])
            
        # Generate 1000 threats
        for _ in range(1000):
            ip = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
            anomaly = random.choice(anomalies)
            if anomaly["payload"]:
                log = f"{ip} REQ=POST {anomaly['endpoint']} PAYLOAD='{anomaly['payload']}' STATUS=400 MSG='{anomaly['payload']}'"
            else:
                log = f"{ip} REQ=GET {anomaly['endpoint']} STATUS=403"
            writer.writerow([log, anomaly["label"]])

    print("Generated 6000 labeled records at data/training_data.csv")

if __name__ == "__main__":
    generate_labeled_data()
