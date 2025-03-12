#!/usr/bin/env python3
import argparse
import os

MIN_SIZE = 512

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

    lonely_onion = []
    for (n, onion, urls) in work:
        folder = os.path.join(args.output, str(n))
        onion_file = os.path.join(folder, "onion")
        if not os.path.exists(onion_file) or os.path.getsize(onion_file) < MIN_SIZE:
            continue

        alone = True
        for (i, url) in enumerate(urls):
            url_file = os.path.join(folder, str(i))
            if not os.path.exists(url_file):
                continue
            
            alone = False
            break
        
        if alone:
            lonely_onion.append(onion)
    
    print(f"found {len(lonely_onion)} lonely onions")
    for onion in lonely_onion:
        print(onion)


parser = argparse.ArgumentParser(description="Visit onion frontpage")
parser.add_argument("-l", "--list", required=True, help="list of urls to visit")
parser.add_argument("-o", "--output", required=True, help="output folder")


args = parser.parse_args()

if __name__ == "__main__":
    main()