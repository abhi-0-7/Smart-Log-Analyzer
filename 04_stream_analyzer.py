import time
import json
import os
import joblib
from datetime import datetime
from kafka import KafkaConsumer

# Load the trained Machine Learning Model (AUTHORITATIVE)
ML_MODEL_PATH = "models/sklearn_rf_pipeline.joblib"
ml_pipeline = None
if os.path.exists(ML_MODEL_PATH):
    ml_pipeline = joblib.load(ML_MODEL_PATH)
    print("Successfully loaded Scikit-Learn Supervised ML Model (Random Forest).")
else:
    print("WARNING: ML Model not found! Run 03_train_ml_model.py first.")
    exit(1)

def analyze_log(line):
    """
    Supervised Machine Learning Detection!
    The AI has learned the language of cyber attacks and predicts the flag directly.
    """
    line_clean = line.strip()
    if not line_clean:
        return None

    # --- True AI Inference ---
    try:
        flag = ml_pipeline.predict([line_clean])[0]
    except Exception:
        flag = "NORMAL"

    reason = "Detected by Random Forest ML Model." if flag != "NORMAL" else "Regular website interaction. ML found no threat."

    return {
        "processing_time": datetime.now().isoformat(),
        "raw_log": line_clean,
        "alert_flag": flag,
        "alert_reason": reason,
        "ml_cluster": 1 if flag != "NORMAL" else 0, # Simplify cluster to just 0 or 1 for UI coloring
        "is_threat": flag != "NORMAL",
    }

def start_kafka_analysis(output_dir):
    print(f"Stream Analyzer connecting to Apache Kafka Topic: soc_logs...")
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        consumer = KafkaConsumer(
            'soc_logs',
            bootstrap_servers=['localhost:9092'],
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        print("Connected! Listening for live Kafka stream...")
    except Exception as e:
        print(f"Failed to connect to Kafka Broker. Is Kafka running? Error: {e}")
        return

    batch_count = 0
    for message in consumer:
        log_entry = message.value.get('log', '')
        result = analyze_log(log_entry)
        if result is None:
            continue

        # Write immediately - no batching, true real-time
        output_file = os.path.join(
            output_dir,
            f"event_{int(time.time()*1000)}_{batch_count}.json"
        )
        with open(output_file, 'w') as out_f:
            out_f.write(json.dumps(result) + "\n")

        batch_count += 1
        cleanup_old_logs(output_dir)

def cleanup_old_logs(output_dir):
    """Keep only the latest 50 processed event files."""
    try:
        files = sorted(
            [os.path.join(output_dir, f) for f in os.listdir(output_dir) if f.endswith('.json')],
            key=os.path.getmtime
        )
        if len(files) > 50:
            for f in files[:-50]:
                try:
                    os.remove(f)
                except Exception:
                    pass
    except Exception:
        pass

if __name__ == "__main__":
    output_dir = "data/processed_logs"
    try:
        start_kafka_analysis(output_dir)
    except KeyboardInterrupt:
        print("Stopping Stream Analyzer.")
