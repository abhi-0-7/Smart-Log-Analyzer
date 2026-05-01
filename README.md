# Smart Log Analyzer for Scalable System Monitoring

![Dashboard Demo](https://img.shields.io/badge/Status-Complete-success)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![PySpark](https://img.shields.io/badge/PySpark-3.5-orange)
![Flask](https://img.shields.io/badge/Flask-Web%20App-lightgrey)

An end-to-end Big Data analytics pipeline that processes massive server access logs using Apache Spark, detects anomalies, and visualizes insights in real-time via a Flask & Plotly web dashboard. Built as an academic project for the Department of Artificial Intelligence and Machine Learning.

## 🌟 Key Features
- **High-Volume Data Processing**: Utilizes Apache Spark to parse and aggregate millions of unstructured HTTP access logs efficiently.
- **Statistical Anomaly Detection**: Automatically flags anomalous traffic spikes using standard deviation thresholds (Mean + 2 SD).
- **Security & Error Tracking**: Identifies potential malicious actors (IPs) based on extreme request counts and high HTTP 4xx/5xx error rates.
- **Interactive Web Dashboard**: A fully responsive, dark-mode dashboard built with Flask, Tailwind CSS, and Plotly to visualize system health in real-time.

## 🏗️ Architecture & Tech Stack
1. **Data Ingestion**: Raw Apache logs (e.g., NASA HTTP dataset).
2. **Data Engine**: **PySpark** parses Regex, filters, groups, and computes analytics.
3. **Data Storage**: Processed metrics are exported as lightweight CSVs.
4. **Visualization Layer**: **Flask** backend serving **Plotly** interactive graphs on a **Tailwind CSS** frontend.

## 🚀 How to Run the Project Locally

### Prerequisites
- Python 3.8+
- Java (OpenJDK 11 or 17)
- Apache Spark (PySpark)
- Hadoop Winutils (If running on Windows)

### 1. Install Dependencies
```bash
pip install pyspark pandas flask plotly
```

### 2. Add Your Data
Download your server access logs (e.g., Apache/Nginx) and place them inside the `data/raw/` directory. If using the NASA dataset, extract the `.gz` text files there.

### 3. Run the PySpark Processing Engine
This script reads the raw logs, computes the analytics, and generates the reports.
```bash
python scripts/03_spark_processing.py
```

### 4. Start the Web Dashboard
Launch the Flask application to view your analyzed data.
```bash
python dashboard/app.py
```
Open your web browser and navigate to `http://127.0.0.1:5000`.

## 📁 Project Structure
```text
BIG DATA/
│
├── data/
│   ├── raw/                 # Put your heavy raw log files here (ignored by git)
│   └── processed/           # Intermediate processed data
│
├── scripts/
│   └── 03_spark_processing.py # The main PySpark analytics engine
│
├── output/
│   └── reports/             # Generated CSV files consumed by the dashboard
│
├── dashboard/
│   ├── app.py               # Flask backend
│   └── templates/
│       └── index.html       # Web UI with Tailwind and Plotly
│
├── synopsis.md              # Project synopsis and academic documentation
└── README.md                # This file
```

## 🎓 Academic Info
- **Course Code:** AI362IA (Big Data Technologies)
- **Department:** Artificial Intelligence and Machine Learning
- **Team Members:** Abhilash Maiya Y, Biradar Abhishek Mallikarjun, Harsh Agarwal
