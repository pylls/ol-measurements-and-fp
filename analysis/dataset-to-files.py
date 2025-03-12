#!/usr/bin/env python3
import h5py
import numpy as np
import pickle
import os

with h5py.File("onionloc.hdf5", "r") as f:
    for dataset in ["clearnet", "onion", "autoloc", "curl"]:
        print(f"\nProcessing dataset: {dataset}")

        if os.path.exists(dataset):
            print(f"Directory '{dataset}' exists, skipping this dataset...")
            continue
        os.mkdir(dataset)

        raw = f[dataset]
        print(f"Dataset shape for '{dataset}': {raw.shape}")

        tags = list(np.unique(raw["tag"]))
        print(f"Processing {len(tags)} tags for dataset '{dataset}'...")

        for i, tag in enumerate(tags):
            selected_circuits = raw[raw["tag"] == tag]
            selected_circuits = selected_circuits[
                np.argsort(selected_circuits["time_created"])
            ]

            fname = f"{i}.pickle"
            p = os.path.join(dataset, fname)
            print(f"Saving {len(selected_circuits)} circuits to {p}...")
            pickle.dump((tag, selected_circuits), open(p, "wb"))

            print(f"Tag {i + 1}/{len(tags)} done for dataset '{dataset}'")

        print(f"Finished processing dataset: {dataset}")
