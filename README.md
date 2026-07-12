# 🛡️ SmartLogAnalyzer: Enterprise AI-Powered SOC Pipeline

SmartLogAnalyzer is an end-to-end, Big Data cybersecurity pipeline designed to process massive historical log datasets and analyze high-velocity real-time traffic using Artificial Intelligence and Apache Kafka.

## 🚀 Key Features

* **Dual-Mode Processing**: Seamlessly toggle between analyzing massive historical datasets (PySpark-generated) and monitoring live web traffic.
* **Apache Kafka Streaming**: True enterprise message-broker architecture. Web events are produced to a Kafka topic and consumed in real-time by the analyzer.
* **Predictive Machine Learning**: Replaces legacy rule-based engines with a Scikit-Learn **Random Forest Classifier** that predicts the exact cyber threat (SQLi, XSS, DDoS, etc.) based on natural language processing (TF-IDF) of the raw payload.
* **Attack Simulator**: Features a fully functional Target Website (NexGen Store) with a hidden Hacker Terminal, allowing analysts to manually inject 8 specific types of cyber attacks into the live Kafka stream.
* **SOC Dashboard**: A sleek, authenticated dashboard that calculates mathematical event velocity, dynamic threat breakdowns, and real-time ML clustering.

## ⚙️ Architecture

1. **NexGen Web Store (Port 5001)**: The target environment. Generates legitimate HTTP traffic and acts as a **Kafka Producer** to broadcast logs.
2. **Apache Kafka (Port 9092)**: The Big Data message broker. Handles high-throughput log ingestion and decouples the web servers from the analytics engine.
3. **AI Stream Analyzer**: The **Kafka Consumer**. Pulls logs from the broker, vectorizes the text, and feeds it into the Random Forest model for instant threat inference.
4. **SOC Dashboard (Port 5000)**: The front-end interface that polls processed JSON logs and visualizes the network state.

## 🛠️ Setup & Execution

### Prerequisites
* Java 8+ (for Zookeeper/Kafka)
* Python 3.10+
* Apache Kafka (Binaries extracted to `C:\Kafka`)

### Running the Pipeline
1. Start Zookeeper: `.\start_zk.ps1`
2. Start Kafka: `.\start_kafka.ps1`
3. Generate Labeled ML Data: `python generate_labeled_data.py`
4. Train the AI Model: `python 03_train_ml_model.py`
5. Start the Target Website: `python 07_company_website.py` (Runs on Port 5001)
6. Start the AI Stream Analyzer: `python 04_stream_analyzer.py`
7. Start the SOC Dashboard: `python 06_dashboard.py` (Runs on Port 5000)

## 📊 The 8 Detected Threat Vectors
1. SQL Injection (SQLi)
2. Cross-Site Scripting (XSS)
3. Distributed Denial of Service (DDoS) / Rate Limiting
4. Path Traversal
5. Brute Force Authentication
6. Privilege Escalation
7. Cross-Site Request Forgery (CSRF)
8. Application Crash Injections
