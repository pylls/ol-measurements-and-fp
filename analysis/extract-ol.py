#!/usr/bin/env python3
import os
import numpy as np
import pickle

# DF trace representation length
LENGTH = 5000
HALF = int(LENGTH / 2)

KIND_GENERAL = 0
KIND_HSDIR = 1
KIND_INTRO = 2
KIND_REND = 3

FILTERED_DOMAINS = [
    b"securedrop.org",
    b"185.220.103.112",
    b"185.220.103.119",
]

CF_DOMAINS = [
    b"cflaresuje2rb7w2u3w43pn4luxdi6o7oatv6r2zrfb5xvsugj35d2qd.onion",
    b"cflarexljc3rw355ysrkrzwapozws6nre6xsy3n4yrj7taye3uiby3ad.onion",
    b"cflarenuttlfuyn7imozr4atzvfbiw3ezgbdjdldmdx7srterayaozid.onion",
    b"cflareki4v3lh674hq55k3n7xd4ibkwx3pnw67rr3gkpsonjmxbktxyd.onion",
    b"cflareub6dtu7nvs3kqmoigcjdwap2azrkx5zohb2yk7gqjkwoyotwqd.onion",
    b"cflareusni3s7vwhq2f7gc4opsik7aa4t2ajedhzr42ez6uajaywh3qd.onion",
    b"cflareer7qekzp3zeyqvcfktxfrmncse4ilc7trbf6bp6yzdabxuload.onion",
    b"cflares35lvdlczhy3r6qbza5jjxbcplzvdveabhf7bsp7y4nzmn67yd.onion",
    b"cflarejlah424meosswvaeqzb54rtdetr4xva6mq2bm2hfcx5isaglid.onion",
    b"cflare2nge4h4yqr3574crrd7k66lil3torzbisz6uciyuzqc2h2ykyd.onion",
    b"cloudflare.com",
]


def cells2df(cells, length=LENGTH):
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


def extract_ol_format(files, name, MIN_NONZERO_CELLS=200, POSITIVE_CLASS=False):
    labels, dataset = {}, {}
    for i, f in enumerate(files):
        with open(os.path.join(name, f), "rb") as file:
            (tag, selected_circuits) = pickle.load(file)

            fetches = np.unique(selected_circuits["fetch"])
            for f in fetches:
                uuid = f"{name}-{tag}-{f}"
                circuits = selected_circuits[selected_circuits["fetch"] == f]

                # kind -> list of traces
                traces = {}
                for c in circuits:
                    if c["domain"] in FILTERED_DOMAINS or (
                        POSITIVE_CLASS and c["domain"] in CF_DOMAINS
                    ):
                        continue
                    if c["kind"] == KIND_GENERAL:
                        if is_dir_circuit(c["cells"]):
                            continue
                    t = cells2df(
                        c["cells"][np.vectorize(lambda cell: cell[3] != 16)(c["cells"])]
                    )
                    if c["kind"] not in traces:
                        traces[c["kind"]] = []
                    traces[c["kind"]].append(t)

                if KIND_GENERAL not in traces or KIND_REND not in traces:
                    # only want fetches that might have done something
                    continue

                # can the attacker collect correctly labeled data on its own? yes!
                if POSITIVE_CLASS:
                    largest_general = get_max_nonzero_trace(traces[KIND_GENERAL])
                    largest_general_len = get_trace_length(largest_general)
                    largest_rend = get_max_nonzero_trace(traces[KIND_REND])
                    largest_rend_len = get_trace_length(largest_rend)

                    # make sure we have at least X non-zero cells on both loads
                    if (
                        largest_general_len < MIN_NONZERO_CELLS
                        or largest_rend_len < MIN_NONZERO_CELLS
                    ):
                        continue

                    labels[uuid] = tag
                    # concatenate the the first HALF cells from the traces
                    dataset[uuid] = np.concatenate(
                        (largest_general[:, :HALF], largest_rend[:, :HALF]), axis=1
                    )
                else:
                    # negative class: we use every possible combination of
                    # general and rend circuits
                    i = 0
                    for general in traces[KIND_GENERAL]:
                        for rend in traces[KIND_REND]:
                            ID = f"{uuid}-{i}"
                            labels[ID] = tag
                            dataset[ID] = np.concatenate(
                                (general[:, :HALF], rend[:, :HALF]), axis=1
                            )
                            i += 1
                    pass

    return labels, dataset


def extract_negative_autoloc(clearnet_files, onion_files, MIN_NONZERO_CELLS=0):
    # find all clearnet general circuits (and not dir)
    clearnet_general_circuits = []
    for i, f in enumerate(clearnet_files):
        with open(os.path.join("clearnet", f), "rb") as file:
            (tag, selected_circuits) = pickle.load(file)

            fetches = np.unique(selected_circuits["fetch"])
            for f in fetches:
                circuits = selected_circuits[selected_circuits["fetch"] == f]
                traces = {}
                for c in circuits:
                    if c["kind"] == KIND_GENERAL:
                        if is_dir_circuit(c["cells"]):
                            continue
                        t = cells2df(
                            c["cells"][
                                np.vectorize(lambda cell: cell[3] != 16)(c["cells"])
                            ]
                        )
                        if c["kind"] not in traces:
                            traces[c["kind"]] = []
                        traces[c["kind"]].append(t)
                        if get_trace_length(t) >= MIN_NONZERO_CELLS:
                            clearnet_general_circuits.append(t)

    # find all onion rend circuits
    onion_rend_circuits = []
    for i, f in enumerate(onion_files):
        with open(os.path.join("onion", f), "rb") as file:
            (tag, selected_circuits) = pickle.load(file)

            fetches = np.unique(selected_circuits["fetch"])
            for f in fetches:
                circuits = selected_circuits[selected_circuits["fetch"] == f]
                traces = {}
                for c in circuits:
                    if c["kind"] == KIND_REND:
                        t = cells2df(
                            c["cells"][
                                np.vectorize(lambda cell: cell[3] != 16)(c["cells"])
                            ]
                        )
                        if c["kind"] not in traces:
                            traces[c["kind"]] = []
                        traces[c["kind"]].append(t)
                        if get_trace_length(t) >= MIN_NONZERO_CELLS:
                            onion_rend_circuits.append(t)

    # shuffle both
    np.random.shuffle(clearnet_general_circuits)
    np.random.shuffle(onion_rend_circuits)

    # merge
    labels, dataset = {}, {}
    for i in range(min(len(clearnet_general_circuits), len(onion_rend_circuits))):
        uuid = f"negative-{i}"
        labels[uuid] = 0
        dataset[uuid] = np.concatenate(
            (
                clearnet_general_circuits[i][:, :HALF],
                onion_rend_circuits[i][:, :HALF],
            ),
            axis=1,
        )

    return labels, dataset


def get_pickle_list(dir):
    return sorted([f for f in os.listdir(dir) if f.endswith(".pickle")])


def save(name, m, labels, dataset):
    FNAME = f"{name}-{m}.npz"
    np.savez_compressed(FNAME, labels=labels, dataset=dataset)
    print(f"saved to {FNAME}")


print("listing files...")
autoloc_files = get_pickle_list("autoloc")
clearnet_files = get_pickle_list("clearnet")
onion_files = get_pickle_list("onion")

min_positive_sizes = [30, 35, 50, 75, 100]
for m in min_positive_sizes:
    print(f"extracting autoloc, min size {m}...")
    labels, dataset = extract_ol_format(autoloc_files, "autoloc", m, True)
    save("autoloc", m, labels, dataset)

print("extracting clearnet...")
labels, dataset = extract_ol_format(clearnet_files, "clearnet", 0, False)
save("clearnet-ol", 0, labels, dataset)

print("extracting onion...")
labels, dataset = extract_ol_format(onion_files, "onion", 0, False)
save("onion-ol", 0, labels, dataset)

print("extracting negative autoloc...")
labels, dataset = extract_negative_autoloc(clearnet_files, onion_files, 100)
save("negative-ol", 100, labels, dataset)
