#!/usr/bin/env python3
import argparse
import os
import subprocess
import random
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm

CLOUDFLARE_ERROR = "Attention Required! | Cloudflare"

def main():
    work = []
    with open(args.list, "r") as f:
        urls = f.readlines()
        for (n, line) in enumerate(urls):
            line = line.strip().split(" ")
            onion = line[0]
            urls = line[1:]
            work.append((n, onion, urls))
    
    print(f"got {len(work)} onions to visit")

    total_urls = sum(len(urls) for _, _, urls in work)
    print(f"with {total_urls} clearnet URLs to visit")

    random.shuffle(work)
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        list(tqdm(executor.map(worker, work), total=len(work)))

def worker(args):
    n, onion, urls = args
    do_work(n, onion, urls)

def do_work(n, onion, urls):
    # create folder output/n if it doesn't exist
    folder = os.path.join(args.output, str(n))
    if not os.path.exists(folder):
        os.makedirs(folder)

    # should we collect onion?
    onion_file = os.path.join(folder, "onion")
    if not os.path.exists(onion_file) or os.path.getsize(onion_file) == 0:
        attempt_visit(onion, onion_file)

    # without onion, no point in collecting clearnet
    if not os.path.exists(onion_file) or os.path.getsize(onion_file) == 0:
        return

    # for each url, should we collect?
    for (i, url) in enumerate(urls):
        url_file = os.path.join(folder, str(i))
        try:
            if (not os.path.exists(url_file) or
                os.path.getsize(url_file) == 0 or
                CLOUDFLARE_ERROR in open(url_file).read()):
                attempt_visit(url, url_file)
        except:
            pass

def attempt_visit(site, result_file):
    # http://site if onion, otherwise https://site
    full_url = "http://" + site if site.endswith(".onion") else "https://" + site

    # execute: torify curl -L <full_url> -o <result_file>
    cmd = ["timeout", f"{args.timeout}", "torify", "curl", "-L", full_url, "-o", result_file]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()

# we use the file system to synchronize between processes, run multiple times to
# eventually get all the data

parser = argparse.ArgumentParser(description="Visit onion frontpage")
parser.add_argument("-l", "--list", required=True, help="list of urls to visit")
parser.add_argument("-o", "--output", required=True, help="output folder")
parser.add_argument("-t", "--timeout", type=int, default=30, help="timeout in seconds")
parser.add_argument("-w", "--workers", type=int, default=20, help="number of workers")

args = parser.parse_args()

if __name__ == "__main__":
    main()