import os
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline

def train_ml_model():
    data_path = "data/training_data.csv"
    model_output_path = "models/sklearn_rf_pipeline.joblib"
    
    print(f"Loading labeled training data from {data_path}...")
    
    if not os.path.exists(data_path):
        print(f"Error: {data_path} not found. Run generate_labeled_data.py first.")
        return
        
    df = pd.read_csv(data_path)
    
    print(f"Training Supervised Random Forest Model on {len(df)} logs...")
    
    # ML Pipeline: TF-IDF + Random Forest
    # The AI will learn to predict the exact string label ("NORMAL" or "CRITICAL: SQL Injection" etc.)
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(max_features=1000, stop_words='english')),
        ('rf', RandomForestClassifier(n_estimators=100, random_state=42))
    ])
    
    pipeline.fit(df['log_text'], df['label'])
    
    os.makedirs(os.path.dirname(model_output_path), exist_ok=True)
    joblib.dump(pipeline, model_output_path)
    
    print(f"Successfully trained and saved Random Forest model to {model_output_path}")

if __name__ == "__main__":
    train_ml_model()
