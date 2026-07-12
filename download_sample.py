import urllib.request
import os

def download_sample():
    url = "https://raw.githubusercontent.com/logpai/loghub/master/Thunderbird/Thunderbird_2k.log"
    output_dir = r"C:\Users\Abhishek\Documents\BIG DATA\SmartLogAnalyzer\data"
    output_file = os.path.join(output_dir, "Thunderbird_sample.log")
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    print(f"Downloading Thunderbird 2k sample to {output_file}...")
    urllib.request.urlretrieve(url, output_file)
    print("Download complete!")

if __name__ == "__main__":
    download_sample()
