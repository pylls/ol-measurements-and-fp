#!/usr/bin/env python3
import numpy as np
import os
import pickle

KIND_GENERAL = 0
KIND_HSDIR = 1
KIND_INTRO = 2
KIND_REND = 3


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


def process_kinds(kinds, uuid, tag, traces, labels, dataset):
    for kind in kinds:
        if kind in traces:
            for i, t in enumerate(traces[kind]):
                ID = f"{uuid}-{kind}-{i}"
                labels[ID] = tag
                dataset[ID] = t


def extract_dataset(kinds, files, name):
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
                    if c["kind"] == KIND_GENERAL:
                        if is_dir_circuit(c["cells"]):
                            continue
                    t = cells2df(
                        c["cells"][np.vectorize(lambda cell: cell[3] != 16)(c["cells"])]
                    )
                    if c["kind"] not in traces:
                        traces[c["kind"]] = []
                    traces[c["kind"]].append(t)

                process_kinds(kinds, uuid, tag, traces, labels, dataset)

    return labels, dataset


def get_pickle_list(dir):
    return sorted([f for f in os.listdir(dir) if f.endswith(".pickle")])


print("listing files...")
clearnet_files = get_pickle_list("clearnet")
onion_files = get_pickle_list("onion")
curl_files = get_pickle_list("curl")

# general
print("extracting clearnet-only-general.npz...")
labels, dataset = extract_dataset([KIND_GENERAL], clearnet_files, "clearnet")
np.savez_compressed("clearnet-only-general.npz", labels=labels, dataset=dataset)
print("saved to clearnet-only-general.npz")

print("extracting clearnet-no-general.npz...")
labels, dataset = extract_dataset(
    [KIND_HSDIR, KIND_INTRO, KIND_REND], clearnet_files, "clearnet"
)
np.savez_compressed("clearnet-no-general.npz", labels=labels, dataset=dataset)
print("saved to clearnet-no-general.npz")

# hsdir
print("extracting onion-only-hsdir.npz...")
labels, dataset = extract_dataset([KIND_HSDIR], onion_files, "onion")
np.savez_compressed("onion-only-hsdir.npz", labels=labels, dataset=dataset)
print("saved to onion-only-hsdir.npz")

print("extracting onion-no-hsdir.npz...")
labels, dataset = extract_dataset(
    [KIND_GENERAL, KIND_INTRO, KIND_REND], onion_files, "onion"
)
np.savez_compressed("onion-no-hsdir.npz", labels=labels, dataset=dataset)
print("saved to onion-no-hsdir.npz")

# intro
print("extracting onion-only-intro.npz...")
labels, dataset = extract_dataset([KIND_INTRO], onion_files, "onion")
np.savez_compressed("onion-only-intro.npz", labels=labels, dataset=dataset)
print("saved to onion-only-intro.npz")

print("extracting onion-no-intro.npz...")
labels, dataset = extract_dataset(
    [KIND_GENERAL, KIND_HSDIR, KIND_REND], onion_files, "onion"
)
np.savez_compressed("onion-no-intro.npz", labels=labels, dataset=dataset)
print("saved to onion-no-intro.npz")

# rend
print("extracting onion-only-rend.npz...")
labels, dataset = extract_dataset([KIND_REND], onion_files, "onion")
np.savez_compressed("onion-only-rend.npz", labels=labels, dataset=dataset)
print("saved to onion-only-rend.npz")

print("extracting onion-no-rend.npz...")
labels, dataset = extract_dataset(
    [KIND_GENERAL, KIND_HSDIR, KIND_INTRO], onion_files, "onion"
)
np.savez_compressed("onion-no-rend.npz", labels=labels, dataset=dataset)
print("saved to onion-no-rend.npz")

# curl (ok, not circuit fingerprinting, but we just need to extract it
# somewhere)
print("extracting curl-only-general.npz...")
labels, dataset = extract_dataset([KIND_GENERAL], curl_files, "curl")
np.savez_compressed("curl-only-general.npz", labels=labels, dataset=dataset)
print("saved to curl-only-general.npz")