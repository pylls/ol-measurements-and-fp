#!/usr/bin/env python3
import argparse
import os
import Levenshtein

MIN_SIMILARITY = 0.9
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
    
    print(f"got {len(work)} onions")

    total_urls = sum(len(urls) for _, _, urls in work)
    print(f"with {total_urls} clearnet URLs")

    mirrored = []
    for (n, onion, urls) in work:
        folder = os.path.join(args.output, str(n))
        onion_file = os.path.join(folder, "onion")
        if not os.path.exists(onion_file) or os.path.getsize(onion_file) < MIN_SIZE:
            continue

        o = "empty"
        try:
            o = open(onion_file).read().strip()
        except:
            print(f"ERROR reading onion file {onion_file}")
            continue

        matches = []
        for (i, url) in enumerate(urls):
            url_file = os.path.join(folder, str(i))
            if not os.path.exists(url_file) or os.path.getsize(url_file) < MIN_SIZE:
                continue
            
            try:
                u = open(url_file).read().strip()
                if strings_are_similar(o, u):
                    matches.append(url)
            except:
                print(f"ERROR reading url file {url_file}")
                continue
        
        if len(matches) > 0:
            mirrored.append((onion, matches))
    
    print(f"found {len(mirrored)} mirrored onions")
    for (onion, matches) in mirrored:
        # matches is now a list, turn it into a string with spaces
        m = " ".join(matches)
        print(f"{onion} {m}")

def strings_are_similar(str1, str2, threshold=MIN_SIMILARITY):
    return Levenshtein.ratio(str1, str2) >= threshold

parser = argparse.ArgumentParser(description="Visit onion frontpage")
parser.add_argument("-l", "--list", required=True, help="list of urls to visit")
parser.add_argument("-o", "--output", required=True, help="output folder")
args = parser.parse_args()

if __name__ == "__main__":
    main()