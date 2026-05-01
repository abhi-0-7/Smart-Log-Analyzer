"""
Smart Log Analyzer - Apache Spark Processing Engine
=====================================================
Parses NASA HTTP access logs using PySpark, performs:
  1. Log parsing (regex extraction of IP, timestamp, method, endpoint, status, size)
  2. Error detection (4xx and 5xx status codes)
  3. Top IP / user pattern analysis
  4. Anomaly detection (statistical - z-score based)
  5. Hourly traffic analysis
  6. Endpoint popularity analysis

All results are saved as CSV files for the web dashboard.
"""

import os
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    regexp_extract, col, count, desc, avg, stddev, sum as spark_sum,
    when, lit, round as spark_round, udf, concat_ws
)
from pyspark.sql.types import StringType, TimestampType
from datetime import datetime

# ============================================================
# CONFIGURATION
# ============================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
OUTPUT_DIR = os.path.join(BASE_DIR, "output", "reports")

# Ensure output directories exist
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Log files
LOG_FILES = [
    os.path.join(RAW_DATA_DIR, "NASA_access_log_Jul95"),
    os.path.join(RAW_DATA_DIR, "NASA_access_log_Aug95"),
]

# ============================================================
# SPARK SESSION
# ============================================================
print("=" * 60)
print("  SMART LOG ANALYZER - Spark Processing Engine")
print("=" * 60)
print(f"\nInitializing Spark session...")

spark = SparkSession.builder \
    .appName("SmartLogAnalyzer") \
    .master("local[*]") \
    .config("spark.driver.memory", "4g") \
    .config("spark.sql.shuffle.partitions", "8") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")
print(f"Spark session created: {spark.version}")

# ============================================================
# MODULE 1: LOG PARSING
# ============================================================
print("\n" + "-" * 60)
print("  MODULE 1: Parsing Raw Log Files")
print("-" * 60)

# Read all log files
raw_logs = spark.read.text(LOG_FILES)
total_raw = raw_logs.count()
print(f"Total raw log lines loaded: {total_raw:,}")

# Apache Combined Log Format regex parsing
# Format: host - - [timestamp] "method endpoint protocol" status size
LOG_PATTERN = r'^(\S+) - - \[(\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2}) -\d{4}\] "(\S+)\s+(\S+)\s*\S*" (\d{3}) (\S+)'

parsed = raw_logs.select(
    regexp_extract('value', LOG_PATTERN, 1).alias('ip'),
    regexp_extract('value', LOG_PATTERN, 2).alias('timestamp'),
    regexp_extract('value', LOG_PATTERN, 3).alias('method'),
    regexp_extract('value', LOG_PATTERN, 4).alias('endpoint'),
    regexp_extract('value', LOG_PATTERN, 5).cast('int').alias('status'),
    regexp_extract('value', LOG_PATTERN, 6).alias('size_str'),
)

# Clean: filter out lines that didn't parse, convert size
parsed = parsed.filter(col('ip') != '') \
    .withColumn('size', when(col('size_str') == '-', 0).otherwise(col('size_str').cast('int'))) \
    .drop('size_str')

# Extract date and hour components for analysis
parsed = parsed \
    .withColumn('day', regexp_extract('timestamp', r'^(\d{2}/\w{3}/\d{4})', 1)) \
    .withColumn('hour', regexp_extract('timestamp', r':(\d{2}):\d{2}:\d{2}', 1)) \
    .withColumn('month', regexp_extract('timestamp', r'/(\w{3})/', 1))

# Cache for reuse across modules
parsed.cache()
total_parsed = parsed.count()
parse_rate = (total_parsed / total_raw) * 100
print(f"Successfully parsed: {total_parsed:,} lines ({parse_rate:.1f}%)")
print(f"Failed to parse: {total_raw - total_parsed:,} lines")

# Instead of saving the full 3.4M row dataset, we only save aggregated data for the dashboard
# to keep things fast and avoid Hadoop Windows IO errors.
# parsed_csv_path = os.path.join(PROCESSED_DIR, "parsed_logs.csv")
# parsed.coalesce(1).write.mode("overwrite").option("header", "true").csv(parsed_csv_path)
print(f"Skipping saving full parsed dataset to save space.")

# ============================================================
# MODULE 2: ERROR DETECTION
# ============================================================
print("\n" + "-" * 60)
print("  MODULE 2: Error Detection & Analysis")
print("-" * 60)

# Overall status code distribution
status_dist = parsed.groupBy('status') \
    .agg(count('*').alias('count')) \
    .orderBy(desc('count'))

print("\nStatus Code Distribution:")
status_dist.show(20, truncate=False)

# Save status distribution
status_csv = os.path.join(OUTPUT_DIR, "status_distribution.csv")
status_dist.toPandas().to_csv(status_csv, index=False)

# Error logs (4xx and 5xx)
errors = parsed.filter(col('status') >= 400)
error_count = errors.count()
error_rate = (error_count / total_parsed) * 100
print(f"Total errors (4xx + 5xx): {error_count:,} ({error_rate:.2f}%)")

# Error breakdown by type
error_breakdown = errors.withColumn(
    'error_type',
    when(col('status').between(400, 499), 'Client Error (4xx)')
    .when(col('status').between(500, 599), 'Server Error (5xx)')
).groupBy('error_type', 'status') \
    .agg(count('*').alias('count')) \
    .orderBy(desc('count'))

print("\nError Breakdown:")
error_breakdown.show(20, truncate=False)

# Save error breakdown
error_csv = os.path.join(OUTPUT_DIR, "error_breakdown.csv")
error_breakdown.toPandas().to_csv(error_csv, index=False)

# Errors by day (for time-series chart)
errors_by_day = parsed.filter(col('status') >= 400) \
    .groupBy('day') \
    .agg(count('*').alias('error_count')) \
    .orderBy('day')

errors_day_csv = os.path.join(OUTPUT_DIR, "errors_by_day.csv")
errors_by_day.toPandas().to_csv(errors_day_csv, index=False)

# Top error-producing endpoints
error_endpoints = errors.groupBy('endpoint', 'status') \
    .agg(count('*').alias('count')) \
    .orderBy(desc('count')) \
    .limit(30)

print("\nTop Error-Producing Endpoints:")
error_endpoints.show(15, truncate=False)

error_ep_csv = os.path.join(OUTPUT_DIR, "error_endpoints.csv")
error_endpoints.toPandas().to_csv(error_ep_csv, index=False)

# ============================================================
# MODULE 3: TOP IPs / USER PATTERN ANALYSIS
# ============================================================
print("\n" + "-" * 60)
print("  MODULE 3: IP / User Pattern Analysis")
print("-" * 60)

# Top 50 most active IPs
top_ips = parsed.groupBy('ip') \
    .agg(
        count('*').alias('total_requests'),
        spark_sum(when(col('status') >= 400, 1).otherwise(0)).alias('error_requests'),
        spark_sum(col('size')).alias('total_bytes'),
    ) \
    .withColumn('error_rate', spark_round(col('error_requests') / col('total_requests') * 100, 2)) \
    .orderBy(desc('total_requests')) \
    .limit(50)

print("\nTop 20 Most Active IPs:")
top_ips.show(20, truncate=False)

# Save top IPs
top_ips_csv = os.path.join(OUTPUT_DIR, "top_ips.csv")
top_ips.toPandas().to_csv(top_ips_csv, index=False)

# Suspicious IPs: high request count OR high error rate
unique_ips = parsed.groupBy('ip').agg(count('*').alias('total_requests'))
total_unique = unique_ips.count()
print(f"\nTotal unique IPs/hosts: {total_unique:,}")

suspicious = parsed.groupBy('ip') \
    .agg(
        count('*').alias('total_requests'),
        spark_sum(when(col('status') >= 400, 1).otherwise(0)).alias('error_requests'),
    ) \
    .withColumn('error_rate', spark_round(col('error_requests') / col('total_requests') * 100, 2)) \
    .filter(
        (col('total_requests') > 1000) | (col('error_rate') > 50)
    ) \
    .orderBy(desc('total_requests'))

print(f"Suspicious IPs (>1000 requests OR >50% error rate): {suspicious.count()}")
suspicious.show(20, truncate=False)

suspicious_csv = os.path.join(OUTPUT_DIR, "suspicious_ips.csv")
suspicious.toPandas().to_csv(suspicious_csv, index=False)

# ============================================================
# MODULE 4: ANOMALY DETECTION
# ============================================================
print("\n" + "-" * 60)
print("  MODULE 4: Anomaly Detection (Statistical)")
print("-" * 60)

# Hourly traffic volume
hourly_traffic = parsed.groupBy('day', 'hour') \
    .agg(count('*').alias('request_count')) \
    .orderBy('day', 'hour')

# Calculate statistics for anomaly threshold
stats = hourly_traffic.select(
    avg('request_count').alias('mean'),
    stddev('request_count').alias('std')
).collect()[0]

mean_val = stats['mean']
std_val = stats['std'] if stats['std'] else 0
threshold_high = mean_val + 2 * std_val
threshold_low = max(0, mean_val - 2 * std_val)

print(f"Hourly Traffic Statistics:")
print(f"  Mean requests/hour: {mean_val:,.0f}")
print(f"  Std deviation: {std_val:,.0f}")
print(f"  Anomaly threshold (high): {threshold_high:,.0f}")
print(f"  Anomaly threshold (low): {threshold_low:,.0f}")

# Tag anomalies
hourly_with_anomaly = hourly_traffic.withColumn(
    'is_anomaly',
    when(col('request_count') > threshold_high, 'HIGH')
    .when(col('request_count') < threshold_low, 'LOW')
    .otherwise('NORMAL')
).withColumn('threshold_high', lit(round(threshold_high))) \
 .withColumn('threshold_low', lit(round(threshold_low))) \
 .withColumn('mean', lit(round(mean_val)))

anomalies = hourly_with_anomaly.filter(col('is_anomaly') != 'NORMAL')
print(f"\nAnomalous hours detected: {anomalies.count()}")
anomalies.show(20, truncate=False)

# Save hourly traffic with anomaly flags
hourly_csv = os.path.join(OUTPUT_DIR, "hourly_traffic.csv")
hourly_with_anomaly.toPandas().to_csv(hourly_csv, index=False)

# ============================================================
# MODULE 5: ENDPOINT POPULARITY ANALYSIS
# ============================================================
print("\n" + "-" * 60)
print("  MODULE 5: Endpoint / Resource Analysis")
print("-" * 60)

# Top 30 most requested endpoints
top_endpoints = parsed.groupBy('endpoint') \
    .agg(
        count('*').alias('hits'),
        spark_sum(col('size')).alias('total_bytes'),
    ) \
    .orderBy(desc('hits')) \
    .limit(30)

print("\nTop 15 Most Requested Endpoints:")
top_endpoints.show(15, truncate=False)

top_ep_csv = os.path.join(OUTPUT_DIR, "top_endpoints.csv")
top_endpoints.toPandas().to_csv(top_ep_csv, index=False)

# HTTP method distribution
method_dist = parsed.groupBy('method') \
    .agg(count('*').alias('count')) \
    .orderBy(desc('count'))

print("\nHTTP Method Distribution:")
method_dist.show(truncate=False)

method_csv = os.path.join(OUTPUT_DIR, "method_distribution.csv")
method_dist.toPandas().to_csv(method_csv, index=False)

# Daily traffic volume (for time-series)
daily_traffic = parsed.groupBy('day') \
    .agg(
        count('*').alias('total_requests'),
        spark_sum(when(col('status') >= 400, 1).otherwise(0)).alias('errors'),
        spark_sum(col('size')).alias('total_bytes'),
    ) \
    .orderBy('day')

daily_csv = os.path.join(OUTPUT_DIR, "daily_traffic.csv")
daily_traffic.toPandas().to_csv(daily_csv, index=False)

# ============================================================
# MODULE 6: SUMMARY STATISTICS
# ============================================================
print("\n" + "-" * 60)
print("  MODULE 6: Summary Statistics")
print("-" * 60)

# Compute summary
success_count = parsed.filter(col('status').between(200, 299)).count()
redirect_count = parsed.filter(col('status').between(300, 399)).count()
client_error = parsed.filter(col('status').between(400, 499)).count()
server_error = parsed.filter(col('status').between(500, 599)).count()

summary_data = [
    ("Total Log Entries", str(total_parsed)),
    ("Unique IPs/Hosts", str(total_unique)),
    ("Successful (2xx)", str(success_count)),
    ("Redirects (3xx)", str(redirect_count)),
    ("Client Errors (4xx)", str(client_error)),
    ("Server Errors (5xx)", str(server_error)),
    ("Overall Error Rate", f"{error_rate:.2f}%"),
    ("Anomalous Hours", str(anomalies.count())),
    ("Suspicious IPs", str(suspicious.count())),
    ("Mean Requests/Hour", f"{mean_val:,.0f}"),
]

summary_df = spark.createDataFrame(summary_data, ["metric", "value"])
summary_csv = os.path.join(OUTPUT_DIR, "summary_stats.csv")
summary_df.toPandas().to_csv(summary_csv, index=False)

print("\n  SUMMARY")
print("  " + "=" * 40)
for metric, value in summary_data:
    print(f"  {metric:<25} {value:>15}")

# ============================================================
# CLEANUP
# ============================================================
print("\n" + "=" * 60)
print("  Processing Complete!")
print("=" * 60)
print(f"\nAll results saved to: {OUTPUT_DIR}")
print("CSV files generated:")
for f in ["status_distribution", "error_breakdown", "errors_by_day",
          "error_endpoints", "top_ips", "suspicious_ips",
          "hourly_traffic", "top_endpoints", "method_distribution",
          "daily_traffic", "summary_stats"]:
    print(f"  - {f}.csv")

spark.stop()
print("\nSpark session stopped. Done!")
