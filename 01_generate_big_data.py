import os
import time
import sys
from datetime import datetime, timedelta

def generate_massive_dataset(input_file, output_dir, target_size_gb=15):
    """
    Reads a sample log file and amplifies it to a target size (in GB)
    by repeating the logs but continuously incrementing the timestamps
    so they look like a continuous, real-world log stream.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    output_file = os.path.join(output_dir, "thunderbird_massive.log")
    target_bytes = target_size_gb * 1024 * 1024 * 1024
    
    print(f"Starting Data Amplification...")
    print(f"Target Size: {target_size_gb} GB ({target_bytes} bytes)")
    print(f"Output File: {output_file}")
    
    if not os.path.exists(input_file):
        print(f"Error: Input file {input_file} not found. Please run download_sample.py first.")
        return

    with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
        base_lines = f.readlines()
        
    if not base_lines:
        print("Error: Input file is empty.")
        return

    current_time = datetime.now()
    bytes_written = 0
    iteration = 0
    
    start_time = time.time()

    with open(output_file, 'w', encoding='utf-8') as out_f:
        while bytes_written < target_bytes:
            # We modify the timestamp of the base lines to simulate moving forward in time
            for line in base_lines:
                # Thunderbird log format usually starts with a dash or a timestamp.
                # Example: - 1131564478 2005.11.09 tbird-admin1 ...
                # To make this fast, we will just prepend a new synthetic timestamp.
                
                current_time += timedelta(milliseconds=10) # 10ms between logs
                # Create a fake realistic prefix
                time_str = current_time.strftime("%Y.%m.%d %H:%M:%S")
                
                # We'll just replace the first 30 chars or so, or simply prepend our time
                # A simple and extremely fast approach:
                new_line = f"[{time_str}] {line}"
                
                out_f.write(new_line)
                bytes_written += len(new_line.encode('utf-8'))
                
                if bytes_written >= target_bytes:
                    break
            
            iteration += 1
            if iteration % 1000 == 0:
                elapsed = time.time() - start_time
                mb_written = bytes_written / (1024 * 1024)
                print(f"Progress: {mb_written:.2f} MB written. Elapsed time: {elapsed:.2f}s")
                
    end_time = time.time()
    print(f"\n--- Amplification Complete ---")
    print(f"Total Size: {bytes_written / (1024*1024*1024):.2f} GB")
    print(f"Time Taken: {end_time - start_time:.2f} seconds")
    print(f"File saved to: {output_file}")

if __name__ == "__main__":
    # Default to 15GB if no argument is passed
    target_gb = 15.0
    if len(sys.argv) > 1:
        target_gb = float(sys.argv[1])
        
    input_sample = r"C:\Users\Abhishek\Documents\BIG DATA\SmartLogAnalyzer\data\Thunderbird_sample.log"
    output_directory = r"C:\Users\Abhishek\Documents\BIG DATA\SmartLogAnalyzer\data\raw_logs"
    
    generate_massive_dataset(input_sample, output_directory, target_gb)
