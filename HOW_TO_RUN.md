# 🏃 How to Run SmartLogAnalyzer

This guide provides step-by-step instructions for starting the entire Enterprise SOC pipeline, training the AI, and demonstrating the real-time cyber attacks.

## 1. Start the Big Data Broker (Apache Kafka)
Before starting any Python scripts, the central message broker must be running to handle the data streams.
Open **PowerShell** in the `SmartLogAnalyzer` directory and start Zookeeper:
```powershell
.\start_zk.ps1
```
Open a **new PowerShell window** and start Kafka:
```powershell
.\start_kafka.ps1
```
*(Leave both of these windows open in the background).*

## 2. Train the Artificial Intelligence
If this is your first time running the project, you must train the Random Forest AI model.
Open a new terminal in the `SmartLogAnalyzer` directory:
```powershell
# 1. Generate the labeled synthetic training dataset (creates training_data.csv)
python generate_labeled_data.py

# 2. Train the Random Forest pipeline
python 03_train_ml_model.py
```
*You should see a message saying "Successfully trained and saved Random Forest model".*

## 3. Start the Pipeline Servers
You need to launch three independent components. You can do this by running them in separate terminal windows, or by running the automated script.

**Option A (Manual - Recommended for Debugging):**
```powershell
# Terminal 1: The Target Website (Producer)
python 07_company_website.py

# Terminal 2: The AI Stream Analyzer (Consumer)
python 04_stream_analyzer.py

# Terminal 3: The SOC Dashboard (UI)
python 06_dashboard.py
```

## 4. How to Demonstrate the Project
1. **Open the Dashboard**: Go to `http://localhost:5000` in your web browser. Register a new Analyst Account and log in.
2. **Toggle Modes**: Explain that the "Historical Dataset" mode processes a massive static log file (like PySpark batch processing). Then, click the toggle to switch to **Live Website** mode. The Event Velocity will drop to 0.
3. **Open the Target Website**: Go to `http://localhost:5001`. 
4. **Generate Normal Traffic**: Click links like *Shop Now* or *Categories*. Notice that the Dashboard on Port 5000 accurately registers these as `NORMAL` events.
5. **Launch an Attack**: On the Website (Port 5001), scroll to the bottom right corner and click the glowing green **Launch Attack Simulator** button. The Hacker Terminal will slide up.
6. **The Climax**: Click "SQL Injection". Switch back to the Dashboard. You will see the AI instantly catch the payload via the Kafka stream, flash the screen red, log the Critical Threat, and dynamically update the Threat Breakdown chart!
