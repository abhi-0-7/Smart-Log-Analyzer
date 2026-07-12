-- 05_hive_analytics.hql
-- Hive script to analyze the processed, machine-learning-classified log data.

-- 1. Create a database for the project
CREATE DATABASE IF NOT EXISTS smart_log_analyzer;
USE smart_log_analyzer;

-- 2. Create an External Table pointing to the Spark output directory
-- Since Spark Streaming wrote the data in Parquet format, we use STORED AS PARQUET
CREATE EXTERNAL TABLE IF NOT EXISTS processed_logs (
    processing_time TIMESTAMP,
    raw_log STRING,
    log_length INT,
    anomaly_cluster INT
)
STORED AS PARQUET
LOCATION 'hdfs://localhost:9000/output/processed_logs/';

-- ==========================================
-- ANALYTICAL QUERIES
-- ==========================================

-- Query 1: Overall Summary of Normal vs Anomalous Logs
-- This helps us understand the baseline error rate in our 15GB massive dataset.
SELECT 
    anomaly_cluster, 
    COUNT(*) as total_logs,
    CASE 
        WHEN anomaly_cluster = 0 THEN 'Likely Normal'
        ELSE 'Potential Anomaly' 
    END as cluster_interpretation
FROM 
    processed_logs
GROUP BY 
    anomaly_cluster
ORDER BY 
    total_logs DESC;

-- Query 2: High-Severity Anomaly Detection
-- Let's say Cluster 3 was identified by our Data Science team as critical system failures.
-- We want to see the exact logs that triggered this classification.
SELECT 
    processing_time, 
    raw_log, 
    log_length
FROM 
    processed_logs
WHERE 
    anomaly_cluster = 3
ORDER BY 
    processing_time DESC
LIMIT 100;

-- Query 3: Time-Series Analysis (Anomalies per Hour)
-- This query shows if there was a sudden spike in anomalies at a specific time.
SELECT 
    HOUR(processing_time) as log_hour, 
    COUNT(*) as anomaly_count
FROM 
    processed_logs
WHERE 
    anomaly_cluster != 0 -- Assuming 0 is the 'normal' cluster
GROUP BY 
    HOUR(processing_time)
ORDER BY 
    anomaly_count DESC;

-- Query 4: Statistical Analysis of Log Lengths
-- Sometimes an anomaly is just an unusually long stack trace.
SELECT 
    anomaly_cluster,
    AVG(log_length) as avg_length,
    MAX(log_length) as max_length,
    MIN(log_length) as min_length
FROM 
    processed_logs
GROUP BY 
    anomaly_cluster;
