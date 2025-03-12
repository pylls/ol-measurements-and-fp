#!/usr/bin/env python3
import os
import numpy as np
import pickle
from collections import Counter


def cells2df(cells, length=512):
    data = np.zeros((1, length), dtype=np.float32)
    cell_directions = cells["direction"].astype(np.float32)
    data[0, : len(cell_directions)] = cell_directions[:length]
    return data


def is_dir_circuit(cells):
    for cell in cells:
        if cell["relay_cmd"] == 13:
            return True
    return False


def get_max_nonzero_trace(traces):
    max_trace = None
    max_trace_len = -1
    for t in traces:
        if get_trace_length(t) > max_trace_len:
            max_trace = t
            max_trace_len = get_trace_length(t)
    return max_trace


def get_trace_length(trace):
    return len(np.nonzero(trace)[0])


KIND_GENERAL = 0
KIND_HSDIR = 1
KIND_INTRO = 2
KIND_REND = 3

FILTERED_DOMAINS = [
    b"securedrop.org",
    b"185.220.103.112",
    b"185.220.103.119",
]

for dataset in ["clearnet", "onion", "autoloc", "curl"]:
    print(f"Dataset {dataset}")
    # in the directory, list all files and filter those that end with ".pickle"
    # then, sort the list of files
    files = sorted([f for f in os.listdir(dataset) if f.endswith(".pickle")])
    print(f"Processing {len(files)} files...")

    stats = {}
    stats["total_fetches"] = 0
    stats["total_circuits"] = 0
    stats["dir"] = 0
    stats["no-general"] = 0
    stats["no-rend"] = 0
    stats["largest-general"] = []
    stats["largest-rend"] = []
    stats["smallest-ol-circ"] = []
    stats["inconsistent-size-below-100"] = 0
    stats["largest-is-rend"] = 0
    stats["largest-is-general"] = 0
    stats["filtered-circuits"] = 0
    stats["rend-per-fetch"] = []
    stats["largest-rend-is-cflare"] = 0

    domains_per_fetch = {}

    for i, f in enumerate(files):
        with open(os.path.join(dataset, f), "rb") as file:
            (tag, selected_circuits) = pickle.load(file)

            fetches = np.unique(selected_circuits["fetch"])
            stats["total_fetches"] += len(fetches)
            for f in fetches:
                uuid = f"{dataset}-{tag}-{f}"
                circuits = selected_circuits[selected_circuits["fetch"] == f]
                stats["total_circuits"] += len(circuits)
                domains = []

                # kind -> list of traces
                traces = {}
                size2domain = {}
                for c in circuits:
                    if c["domain"] not in domains:
                        domains.append(c["domain"])

                        if c["kind"] == KIND_GENERAL:
                            if is_dir_circuit(c["cells"]):
                                stats["dir"] += 1
                                continue

                    if c["domain"] in FILTERED_DOMAINS:
                        stats["filtered-circuits"] += 1
                        continue

                    t = cells2df(
                        c["cells"][np.vectorize(lambda cell: cell[3] != 16)(c["cells"])]
                    )
                    if c["kind"] not in traces:
                        traces[c["kind"]] = []
                    traces[c["kind"]].append(t)
                    size2domain[get_trace_length(t)] = c["domain"]

                domains_per_fetch[uuid] = domains
                stats["rend-per-fetch"].append(
                    len(traces[KIND_REND]) if KIND_REND in traces else 0
                )

                if KIND_GENERAL not in traces:
                    stats["no-general"] += 1
                if KIND_REND not in traces:
                    stats["no-rend"] += 1
                if KIND_GENERAL not in traces or KIND_REND not in traces:
                    # only want fetches that might have done something
                    continue
                largest_general = get_max_nonzero_trace(traces[KIND_GENERAL])
                largest_general_len = get_trace_length(largest_general)
                largest_rend = get_max_nonzero_trace(traces[KIND_REND])
                largest_rend_len = get_trace_length(largest_rend)

                if b"cflare" in size2domain[largest_rend_len]:
                    stats["largest-rend-is-cflare"] += 1

                stats["largest-general"].append(largest_general_len)
                stats["largest-rend"].append(largest_rend_len)
                stats["smallest-ol-circ"].append(
                    min(largest_general_len, largest_rend_len)
                )

                if (
                    largest_general_len < 100 and largest_rend_len < 100
                ) and largest_rend_len > largest_general_len:
                    stats["inconsistent-size-below-100"] += 1

                if largest_rend_len > largest_general_len:
                    stats["largest-is-rend"] += 1
                else:
                    stats["largest-is-general"] += 1

    fetches = stats["total_fetches"]
    circuits = stats["total_circuits"]
    print("")
    print(f"################### stats for dataset {dataset} ###################")
    print("")
    print(f"{fetches} fetches using {circuits} circuits for {len(files)} tags/websites")
    print(f"{stats['dir']} circuits were directory circuits")
    print(f"{stats['no-general']} fetches had no general circuits")
    print(f"{stats['no-rend']} fetches had no rend circuits")
    print(
        f"{stats['inconsistent-size-below-100']} fetches had rend circuits larger than general circuits and both were below 100"
    )
    print(
        f"{stats['largest-is-rend']} fetches had rend circuits larger than general circuits"
    )
    print(
        f"{stats['largest-is-general']} fetches had general circuits larger than rend circuits"
    )

    # average, min, max of rend circuits per fetch
    rend_per_fetch = stats["rend-per-fetch"]
    rend_per_fetch.sort()
    median = rend_per_fetch[len(rend_per_fetch) // 2]
    print(
        f"Average number of rend circuits per fetch: {sum(rend_per_fetch) / fetches:.2f} (median: {median}, min: {min(rend_per_fetch)}, max: {max(rend_per_fetch)})"
    )
    # largest cflare
    print(
        f"{stats['largest-rend-is-cflare']} fetches had the largest rend circuit as cloudflare"
    )

    print(
        f"{stats['filtered-circuits']} circuits were filtered out due to domain in {FILTERED_DOMAINS}"
    )

    # go over each list of domains per fetch and make a list of common domains in all fetches
    common_domains = []
    for fetch in domains_per_fetch.values():
        if len(common_domains) == 0:
            common_domains = fetch
        else:
            common_domains = list(set(common_domains) & set(fetch))
    print(f"Common domains in all fetches: {common_domains}")

    # find the top-20 most common domains in all fetches (20 to capture cloudflare)
    all_domains = [domain for fetch in domains_per_fetch.values() for domain in fetch]
    domain_counter = Counter(all_domains)
    print("Top-20 most common domains:")
    for domain, count in domain_counter.most_common(20):
        print(f"{domain}: {count}")

    # sort largest stats
    stats["largest-general"] = sorted(stats["largest-general"])
    stats["largest-rend"] = sorted(stats["largest-rend"])

    sizes = [
        10,
        25,
        30,
        31,
        32,
        33,
        34,
        35,
        40,
        45,
        50,
        75,
        100,
        200,
        300,
        400,
        500,
        512,
    ]
    # percentage of general and rend circuits that have at least X non-zero cells
    for s in sizes:
        general = len([x for x in stats["largest-general"] if x >= s])
        rend = len([x for x in stats["largest-rend"] if x >= s])
        ol = len([x for x in stats["smallest-ol-circ"] if x >= s])
        # print(f'{general} general circuits and {rend} rend circuits have at least {s} non-zero cells')
        print(
            f"{ol} fetches ({100 * ol / fetches:.1f}%) have at least {s} non-zero cells on both circuits ({general} general and {rend} rend)"
        )
    print("")
