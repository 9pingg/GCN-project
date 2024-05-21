# you have not added the cache clear 
# def clearCacheAndConnections(self):
# self.driver.execute_script("return chrome.benchmarking.clearCache();")
# self.driver.execute_script("return chrome.benchmarking.clearHostResolverCache();")
# self.driver.execute_script("return chrome.benchmarking.clearPredictorCache();")
# self.driver.execute_script("return chrome.benchmarking.closeConnections();")


import numpy as np
import argparse
import subprocess
import json
import time
import os
import matplotlib.pyplot as plt

save_plt_values = {}
save_median_plt_values = {}

def make_dir(newpath):
    print(newpath)
    if not os.path.exists(newpath):
        os.makedirs(newpath)

def dump_plt_values():
    filename = "output.json"
    try:
        with open(filename, 'a') as f:
            json.dump(save_plt_values, f, indent=4)
    except Exception as e:
        print(f"Error occurred while saving to file: {e}")
    filename = "output_per.json"
    try:
        with open(filename, 'w') as f:
            json.dump(save_median_plt_values, f, indent=4)
    except Exception as e:
        print(f"Error occurred while saving to file: {e}")

def parse_output():
    
    k1 = None
    k2 = None

    for key, value in save_plt_values.items():
        if hasattr(value, '__len__') and len(value) == 3:
            if k1 is None:
                k1 = key
            elif k2 is None:
                k2 = key

    for key, value in save_plt_values.items():
        if hasattr(value, '__len__'):
            median_value = np.median(value)
            save_plt_values[key] = median_value
    if k1 is not None and k2 is not None:
        v1 = save_plt_values[k1]
        v2 = save_plt_values[k2]
        per =  100 * (v2 - v1) / v1
        per = -1.0 * per
        k1 = k1.removesuffix('_tcp.har')
        k1 = k1.removeprefix('./har_output/')    
        save_median_plt_values[k1] = per
    print(save_plt_values)
    print(save_median_plt_values)

def save_output(plt, outFile):
    if outFile not in save_plt_values:
        save_plt_values[outFile] = [plt]
    else:
        save_plt_values[outFile].append(plt)
    
def read_har_file(outFile):
    try:
        with open(outFile, 'r') as f:
            j = json.load(f)
            plt = j['log']['pages'][0]['pageTimings']['onLoad']
            save_output(plt, outFile)
    except Exception as e:
        print(f"error {e} for file {outFile}")
    
parser = argparse.ArgumentParser(description='Run Chrome headless command multiple times.')
parser.add_argument('-n', '--times', type=int, default=3, help='Number of times to run the commands.')

args = parser.parse_args()

# taken from orignal script.
commonOptions = [
    '--no-first-run',
    '--disable-background-networking',
    '--disable-client-side-phishing-detection',
    '--disable-component-update',
    '--disable-default-apps',
    '--disable-hang-monitor',
    '--disable-popup-blocking',
    '--disable-prompt-on-repost',
    '--disable-sync',
    '--disable-web-resources',
    '--metrics-recording-only',
    '--password-store=basic',
    '--safebrowsing-disable-auto-update',
    '--use-mock-keychain',
    '--ignore-certificate-errors',
    '--user-data-dir=/tmp/chrome-profile'
]
# to clear cache
clearCacheOptions = ['--enable-benchmarking', 
                    '--enable-net-benchmarking',
                    '--ignore-certificate-errors-spki-list="gtB+hrd4WP/yiaEjzopJGHy7yWKGqazoxiINe/sM7DE="',
                    '--no-proxy-server https://34.120.76.195/',
                    
                    ]
                    

clearCacheOptionsQuic =['--enable-quic',
                    '--no-proxy-server',
                    '--enable-benchmarking', 
                    '--enable-net-benchmarking',
                    '--origin-to-force-quic-on=34.120.76.195:443',
                    '--ignore-certificate-errors-spki-list="gtB+hrd4WP/yiaEjzopJGHy7yWKGqazoxiINe/sM7DE=" https://34.120.76.195/']
                    
                    
         


open_chrome_cmd = "google-chrome --remote-debugging-port=9222 " + " ".join(commonOptions) + " ".join(clearCacheOptions)
open_chrome_w_quic = "google-chrome --remote-debugging-port=9222 " + " ".join(commonOptions) + " ".join(clearCacheOptionsQuic)

server = "https://34.120.76.195/"
#url_quic = "https://34.120.76.195/"#quic server IP:port 
# index_type = "10kx100" # give SIZE_COUNT, for index_SIZE_COUNT.html

#index_list = [ "100k", "100kx10", "10k", "10kx100", "10mb", "1mb", "1mbx1", "200k", "200kx5", "500k", "500kx2", "5k", "5kx200"]
index_list = ["5k", "10k", "100k", "200k", "500k", "1mb","10mb", "1mbx1","500kx2", "200kx5", "100kx10", "10kx100", "5kx200" ]

for j in index_list:
    url=""
    url += f"{j}.html"
    for i in range(args.times):
        time.sleep(1)
        open_chrome_process = subprocess.Popen("exec " + open_chrome_cmd + url, shell=True)
        time.sleep(1)
        # print("open chrome process: ",open_chrome_process)
        har_file = f"./har_output/{j}_tcp.har"
        # print("har file ",har_file)
        har_capture_command = f"npx chrome-har-capturer --force --port 9222 -o {har_file} {server}{url}"
        # print("har capture command ",har_capture_command)
        subprocess.run(har_capture_command, shell=True)
        read_har_file(har_file)
        time.sleep(0.5)
        open_chrome_process.kill()


        time.sleep(1)
        open_chrom_w_quic_process = subprocess.Popen("exec " + open_chrome_w_quic + url, shell=True)
        time.sleep(1)
        har_file_quic = f"./har_output_quic/{j}_quic.har"
        har_capture_command_quic = f"npx chrome-har-capturer --force --port 9222 -o {har_file_quic} {server}{url}"
        subprocess.run(har_capture_command_quic, shell=True)
        read_har_file(har_file_quic)
        time.sleep(0.5)
        open_chrom_w_quic_process.kill()
    parse_output()


dump_plt_values()


import matplotlib.ticker
import json



#google-chrome   --user-data-dir=/tmp/chrome-profile  
# --no-proxy-server   x  
# --origin-to-force-quic-on=192.168.29.160:6121  
# --ignore-certificate-errors-spki-list="hr2Rm8j8YeyYWY0EkHBKNsIzd303A6yNKj7qapc9Oiw=" https://192.168.29.160:6121/index.html


# google-chrome   --user-data-dir=/tmp/chrome-profile  
# --no-proxy --ignore-certificate-errors-spki-list="1PF5F32Ra/v7t1hwdb/kxwuFm+CvUq0B6p6Bi+RG0ow=" https://192.168.29.160:9090/mine.html



#google-chrome --user-data-dir=/tmp/chrome-profile --no-proxy-server --enable-quic  --origin-to-force-quic-on=34.120.76.195:443 --ignore-certificate-errors-spki-list="gtB+hrd4WP/yiaEjzopJGHy7yWKGqazoxiINe/sM7DE=" https://34.120.76.195/img.html



