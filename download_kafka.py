import urllib.request
import tarfile
import os

url = "https://archive.apache.org/dist/kafka/3.6.1/kafka_2.13-3.6.1.tgz"
filename = "C:\\Kafka\\kafka.tgz"
extract_path = "C:\\Kafka"

os.makedirs(extract_path, exist_ok=True)

print(f"Downloading Kafka from {url}...")
urllib.request.urlretrieve(url, filename)
print("Download complete.")

print("Extracting...")
with tarfile.open(filename, "r:gz") as tar:
    tar.extractall(path=extract_path)
print("Extraction complete.")
