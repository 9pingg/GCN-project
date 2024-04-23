import argparse
import subprocess
import json
import time

save_plt_values = {}

def make_dir(newpath):
    print(newpath)
    if not os.path.exists(newpath):
        os.makedirs(newpath)

def dump_plt_values():
    filename = "output.txt"
    try:
        with open(filename, 'a') as f:
            json.dump(save_plt_values, f, indent=4)
    except Exception as e:
        print(f"Error occurred while saving to file: {e}")

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
parser.add_argument('-n', '--times', type=int, default=10, help='Number of times to run the commands.')

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
    '--ignore-certificate-errors'
]
# to clear cache
clearCacheOptions = ['--enable-benchmarking', '--enable-net-benchmarking']

open_chrome_cmd = "google-chrome --remote-debugging-port=9222 --headless " + " ".join(commonOptions) + " ".join(clearCacheOptions)

url = "http://192.168.29.160:8000"
index_type = "" # give SIZE_COUNT, for index_SIZE_COUNT.html

for i in range(args.times):
    time.sleep(2)
    open_chrome_process = subprocess.Popen("exec " + open_chrome_cmd, shell=True)
    time.sleep(2)
    
    har_file = f"./har_output/index{index_type}_{i+1}.har"
    url += f"/index{index_type}.html"
    har_capture_command = f"npx chrome-har-capturer --force --port 9222 -o {har_file} {url}"
    subprocess.run(har_capture_command, shell=True)
    read_har_file(har_file)
    
    open_chrome_process.kill()

dump_plt_values()

