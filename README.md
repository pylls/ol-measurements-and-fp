# Onion-Location Measurements and Fingerprinting

Research artifacts for the paper [Onion-Location Measurements and
Fingerprinting](https://petsymposium.org/popets/2025/), PETS 2025, by Paul
Syverson, Rasmus Dahlberg, Tobias Pulls, and Rob Jansen.

In gist, the artifact consist of two open-source tools and datasets that are
available (Section 4 of the paper) as well as dataset analysis (Section 5).

## Dataset collection (Section 4)

The dataset collection took place in four steps.  Step two uses the dataset of
step one as input, step three uses the dataset of step two as input, etc.  Only
the final dataset produced in step four is used for the analysis in Section 5.

### Step 1: collect certificates using ct-sans (Section 4.1.1)

We developed and used [ct-sans](https://git.rgdd.se/ct-sans/about/?h=main): A
tool that downloads certificates from CT logs recognized by Google Chrome,
storing the encountered Subject Alternative Names (SANs) to disk.

Download
[ct-sans/2024-04-03-ct-sans.zip](https://dart.cse.kau.se/ol-measurements-and-fp/ct-sans/2023-04-03-ct-sans.zip).

```bash
sha256sum 2023-04-03-ct-sans.zip
86a5630e1054e26a7781563b1d99b5b638f92b3829d5ebb0f88c2f6611f10a42  2023-04-03-ct-sans.zip
```

### Step 2: identify Onion-Location domains using onion-grab (Section 4.1.2)

We developed and used
[onion-grab](https://gitlab.torproject.org/tpo/onion-services/onion-grab): A
tool that visits a list of domains over HTTPS to see if they have Onion-Location
configured.

Download
[onion-grab/2023-04-03-ct-sans.zip](https://dart.cse.kau.se/ol-measurements-and-fp/onion-grab/2023-04-03-ct-sans.zip)
and download
[onion-grab/2023-04-03-tranco.zip](https://dart.cse.kau.se/ol-measurements-and-fp/onion-grab/2023-04-03-tranco.zip).

```bash
sha256sum 2023-04-03-ct-sans.zip 2023-04-03-tranco.zip
8d476da6077c7bff2c0afbe444344c9549ad0d1b64cacfd525a7c65dec68529c  2023-04-03-ct-sans.zip
1f4a0b4009486bce83262f8e3a58ec50757c3f49305cfa427dadbb10dc4b8c1b  2023-04-03-tranco.zip
```

### Step 3: filter mirrored onions (Section 4.1.3)

With some [python scripts](mirrored-onions/), we identified sites that were
mirrored by comparing the Levenshtein ratio of index.html (and only index.html)
found on clearnet and associated onions from step 2 visited using `torify curl`.

Download
[mirrored-onions-2023-10-31.txt](https://dart.cse.kau.se/ol-measurements-and-fp/mirrored-onions-2023-10-31.txt)
and download
[lonely-onions-2023-10-31.txt](https://dart.cse.kau.se/ol-measurements-and-fp/lonely-onions-2023-10-31.txt).

```bash
sha256sum mirrored-onions-2023-10-31.txt lonely-onions-2023-10-31.txt
73ebe23b78b57b84abee7ae7db9a81de5ce7717686e39d616066e0b1375e263e  mirrored-onions-2023-10-31.txt
cc0d17a552709834a9a0597e1f1ffb3c0704bf1b5b8de239e4cff5471a1f9eb7  lonely-onions-2023-10-31.txt
```

### Step 4: constructing fingerprinting datasets (Section 4.2)

With a modified version of Tor, we collected four datasets of circuits from a
guard relay in the live Tor network: `clearnet`, `onion`, `autoloc`, and `curl`.
We only collected circuits from our own clients. The modifications to Tor are
not shared publicly because we consider this to be in the best interest of Tor.
The paper provides further ethical considerations.

Download the [onionloc.hdf5.zst file of the datasets
here](https://dart.cse.kau.se/ol-measurements-and-fp/onionloc.hdf5.zst).

```bash
sha256sum onionloc.hdf5.zst
9076f013c629d05152d37668540ff222325b3ab2f1fed12d313485b74af5c15e  onionloc.hdf5.zst
```

## Dataset analysis (Section 5)

Here we reproduce key results from the analysis section.

### Dataset processing

Install dependencies in a Python environment of your choice:

```bash
pip install -r requirements.txt
```

Extract the dataset from above (584 MiB packed, 23 GiB extracted):

```bash
zstd -d onionloc.hdf5.zst
sha256sum onionloc.hdf5
a8c69e1c4601e7ce2a46d0122e8eb78d47cfe4b139e4e0e96a58927fe63edead  onionloc.hdf5
```

Run `./analysis/dataset-to-files.py` to extract individual files (each
representing a website visit and all associated circuits) for the `clearnet`,
`onion`, `autoloc`, and `curl` datasets. This is a slow process (hours), sorry,
because `hdf5` is a slow format for random access. If you want to skip this step
and directly go for the extracted files (756 MiB, 17 GiB extracted):

```bash
wget https://dart.cse.kau.se/ol-measurements-and-fp/onionloc.tar.gz
sha256sum onionloc.tar.gz
641f034ec19ced46e49b10aa27ea80bba1fa837466079a64888c5bbd4793dce0  onionloc.tar.gz
```

Similarly, later steps will extract classes for circuit fingerprinting and onion
location fingerprinting. If you want to skip this step and directly get the
resulting files (12 MiB):

```bash
wget https://dart.cse.kau.se/ol-measurements-and-fp/extracted-classes.tar.gz
sha256sum extracted-classes.tar.gz
a17431c11b098c14976b83ea14c1a229afc1ea4b1cf58b37ba880e63a08b4121  extracted-classes.tar.gz
```

### Dataset stats

It is good practice to look at your data. To get a large number of statistics
(some made the paper, some not), run the command below. The total circuit counts
match Table 2 in the paper.

```bash
./dataset-stats.py
Dataset clearnet
Processing 1505 files...

################### stats for dataset clearnet ###################

8996 fetches using 60602 circuits for 1505 tags/websites
7901 circuits were directory circuits
6 fetches had no general circuits
658 fetches had no rend circuits
633 fetches had rend circuits larger than general circuits and both were below 100
838 fetches had rend circuits larger than general circuits
7494 fetches had general circuits larger than rend circuits
Average number of rend circuits per fetch: 1.12 (median: 1, min: 0, max: 11)
7731 fetches had the largest rend circuit as cloudflare
9041 circuits were filtered out due to domain in [b'securedrop.org', b'185.220.103.112', b'185.220.103.119']
Common domains in all fetches: [b'securedrop.org']
Top-20 most common domains:
b'securedrop.org': 8996
b'185.220.103.112': 4482
b'185.220.103.119': 3420
b'cflarexljc3rw355ysrkrzwapozws6nre6xsy3n4yrj7taye3uiby3ad.onion': 973
b'cflareusni3s7vwhq2f7gc4opsik7aa4t2ajedhzr42ez6uajaywh3qd.onion': 958
b'cflareki4v3lh674hq55k3n7xd4ibkwx3pnw67rr3gkpsonjmxbktxyd.onion': 956
b'cflarejlah424meosswvaeqzb54rtdetr4xva6mq2bm2hfcx5isaglid.onion': 942
b'cflareub6dtu7nvs3kqmoigcjdwap2azrkx5zohb2yk7gqjkwoyotwqd.onion': 931
b'cflares35lvdlczhy3r6qbza5jjxbcplzvdveabhf7bsp7y4nzmn67yd.onion': 926
b'cflaresuje2rb7w2u3w43pn4luxdi6o7oatv6r2zrfb5xvsugj35d2qd.onion': 916
b'cflarenuttlfuyn7imozr4atzvfbiw3ezgbdjdldmdx7srterayaozid.onion': 898
b'cflareer7qekzp3zeyqvcfktxfrmncse4ilc7trbf6bp6yzdabxuload.onion': 874
b'cflare2nge4h4yqr3574crrd7k66lil3torzbisz6uciyuzqc2h2ykyd.onion': 850
b'208.109.215.188': 114
b'212.227.171.107': 113
b'171.25.193.77': 102
b'91.228.52.73': 102
b'94.23.76.52': 101
b'79.143.177.192': 100
b'95.211.210.72': 98
8254 fetches (91.8%) have at least 10 non-zero cells on both circuits (8254 general and 8332 rend)
7701 fetches (85.6%) have at least 25 non-zero cells on both circuits (7965 general and 8020 rend)
7590 fetches (84.4%) have at least 30 non-zero cells on both circuits (7942 general and 7914 rend)
7333 fetches (81.5%) have at least 31 non-zero cells on both circuits (7921 general and 7656 rend)
2598 fetches (28.9%) have at least 32 non-zero cells on both circuits (7890 general and 2860 rend)
974 fetches (10.8%) have at least 33 non-zero cells on both circuits (7849 general and 1203 rend)
809 fetches (9.0%) have at least 34 non-zero cells on both circuits (7782 general and 926 rend)
640 fetches (7.1%) have at least 35 non-zero cells on both circuits (7662 general and 798 rend)
124 fetches (1.4%) have at least 40 non-zero cells on both circuits (7165 general and 476 rend)
92 fetches (1.0%) have at least 45 non-zero cells on both circuits (6974 general and 292 rend)
74 fetches (0.8%) have at least 50 non-zero cells on both circuits (6193 general and 271 rend)
30 fetches (0.3%) have at least 75 non-zero cells on both circuits (5606 general and 230 rend)
28 fetches (0.3%) have at least 100 non-zero cells on both circuits (5327 general and 228 rend)
19 fetches (0.2%) have at least 200 non-zero cells on both circuits (4672 general and 216 rend)
15 fetches (0.2%) have at least 300 non-zero cells on both circuits (4299 general and 211 rend)
12 fetches (0.1%) have at least 400 non-zero cells on both circuits (4052 general and 211 rend)
9 fetches (0.1%) have at least 500 non-zero cells on both circuits (3789 general and 205 rend)
9 fetches (0.1%) have at least 512 non-zero cells on both circuits (3765 general and 205 rend)

Dataset onion
Processing 1505 files...

################### stats for dataset onion ###################

9566 fetches using 80734 circuits for 1505 tags/websites
7864 circuits were directory circuits
8064 fetches had no general circuits
278 fetches had no rend circuits
64 fetches had rend circuits larger than general circuits and both were below 100
780 fetches had rend circuits larger than general circuits
722 fetches had general circuits larger than rend circuits
Average number of rend circuits per fetch: 1.92 (median: 2, min: 0, max: 17)
127 fetches had the largest rend circuit as cloudflare
9611 circuits were filtered out due to domain in [b'securedrop.org', b'185.220.103.112', b'185.220.103.119']
Common domains in all fetches: [b'securedrop.org']
Top-20 most common domains:
b'securedrop.org': 9511
b'185.220.103.112': 5055
b'185.220.103.119': 2812
b'cflaresuje2rb7w2u3w43pn4luxdi6o7oatv6r2zrfb5xvsugj35d2qd.onion': 967
b'cflarexljc3rw355ysrkrzwapozws6nre6xsy3n4yrj7taye3uiby3ad.onion': 962
b'cflarenuttlfuyn7imozr4atzvfbiw3ezgbdjdldmdx7srterayaozid.onion': 959
b'cflareki4v3lh674hq55k3n7xd4ibkwx3pnw67rr3gkpsonjmxbktxyd.onion': 947
b'cflareub6dtu7nvs3kqmoigcjdwap2azrkx5zohb2yk7gqjkwoyotwqd.onion': 944
b'cflareusni3s7vwhq2f7gc4opsik7aa4t2ajedhzr42ez6uajaywh3qd.onion': 941
b'cflareer7qekzp3zeyqvcfktxfrmncse4ilc7trbf6bp6yzdabxuload.onion': 935
b'cflares35lvdlczhy3r6qbza5jjxbcplzvdveabhf7bsp7y4nzmn67yd.onion': 923
b'cflarejlah424meosswvaeqzb54rtdetr4xva6mq2bm2hfcx5isaglid.onion': 921
b'cflare2nge4h4yqr3574crrd7k66lil3torzbisz6uciyuzqc2h2ykyd.onion': 916
b'www.googletagmanager.com': 215
b'voanews5aitmne6gs2btokcacixclgfl43cv27sirgbauyyjylwpdtqd.onion': 194
b'185.243.218.110': 177
b'fonts.googleapis.com': 151
b'rferlo2zxgv23tct66v45s5mecftol5vod3hf4rqbipfp46fqu2q56ad.onion': 145
b'tags.tiqcdn.com': 143
b'45.14.233.204': 130
1498 fetches (15.7%) have at least 10 non-zero cells on both circuits (1498 general and 1502 rend)
1478 fetches (15.5%) have at least 25 non-zero cells on both circuits (1489 general and 1490 rend)
1437 fetches (15.0%) have at least 30 non-zero cells on both circuits (1454 general and 1483 rend)
1412 fetches (14.8%) have at least 31 non-zero cells on both circuits (1432 general and 1480 rend)
1334 fetches (13.9%) have at least 32 non-zero cells on both circuits (1410 general and 1407 rend)
1291 fetches (13.5%) have at least 33 non-zero cells on both circuits (1386 general and 1385 rend)
1253 fetches (13.1%) have at least 34 non-zero cells on both circuits (1366 general and 1366 rend)
1236 fetches (12.9%) have at least 35 non-zero cells on both circuits (1354 general and 1359 rend)
1185 fetches (12.4%) have at least 40 non-zero cells on both circuits (1311 general and 1339 rend)
1170 fetches (12.2%) have at least 45 non-zero cells on both circuits (1299 general and 1336 rend)
1136 fetches (11.9%) have at least 50 non-zero cells on both circuits (1290 general and 1305 rend)
860 fetches (9.0%) have at least 75 non-zero cells on both circuits (1029 general and 1258 rend)
754 fetches (7.9%) have at least 100 non-zero cells on both circuits (974 general and 1177 rend)
540 fetches (5.6%) have at least 200 non-zero cells on both circuits (777 general and 1060 rend)
468 fetches (4.9%) have at least 300 non-zero cells on both circuits (674 general and 1024 rend)
396 fetches (4.1%) have at least 400 non-zero cells on both circuits (600 general and 980 rend)
346 fetches (3.6%) have at least 500 non-zero cells on both circuits (537 general and 920 rend)
346 fetches (3.6%) have at least 512 non-zero cells on both circuits (537 general and 913 rend)

Dataset autoloc
Processing 1505 files...

################### stats for dataset autoloc ###################

9027 fetches using 89961 circuits for 1505 tags/websites
8629 circuits were directory circuits
0 fetches had no general circuits
223 fetches had no rend circuits
875 fetches had rend circuits larger than general circuits and both were below 100
1470 fetches had rend circuits larger than general circuits
7334 fetches had general circuits larger than rend circuits
Average number of rend circuits per fetch: 1.99 (median: 2, min: 0, max: 17)
2201 fetches had the largest rend circuit as cloudflare
9089 circuits were filtered out due to domain in [b'securedrop.org', b'185.220.103.112', b'185.220.103.119']
Common domains in all fetches: [b'securedrop.org']
Top-20 most common domains:
b'securedrop.org': 9027
b'185.220.103.112': 4513
b'185.220.103.119': 4118
b'cflarexljc3rw355ysrkrzwapozws6nre6xsy3n4yrj7taye3uiby3ad.onion': 1030
b'cflareusni3s7vwhq2f7gc4opsik7aa4t2ajedhzr42ez6uajaywh3qd.onion': 1011
b'cflareer7qekzp3zeyqvcfktxfrmncse4ilc7trbf6bp6yzdabxuload.onion': 1000
b'cflareub6dtu7nvs3kqmoigcjdwap2azrkx5zohb2yk7gqjkwoyotwqd.onion': 972
b'cflareki4v3lh674hq55k3n7xd4ibkwx3pnw67rr3gkpsonjmxbktxyd.onion': 971
b'cflaresuje2rb7w2u3w43pn4luxdi6o7oatv6r2zrfb5xvsugj35d2qd.onion': 968
b'cflarejlah424meosswvaeqzb54rtdetr4xva6mq2bm2hfcx5isaglid.onion': 956
b'cflarenuttlfuyn7imozr4atzvfbiw3ezgbdjdldmdx7srterayaozid.onion': 945
b'cflares35lvdlczhy3r6qbza5jjxbcplzvdveabhf7bsp7y4nzmn67yd.onion': 939
b'cflare2nge4h4yqr3574crrd7k66lil3torzbisz6uciyuzqc2h2ykyd.onion': 927
b'www.googletagmanager.com': 196
b'voanews5aitmne6gs2btokcacixclgfl43cv27sirgbauyyjylwpdtqd.onion': 189
b'45.14.233.204': 138
b'rferlo2zxgv23tct66v45s5mecftol5vod3hf4rqbipfp46fqu2q56ad.onion': 125
b'tags.tiqcdn.com': 124
b'fonts.googleapis.com': 123
b'66.85.128.218': 113
8702 fetches (96.4%) have at least 10 non-zero cells on both circuits (8702 general and 8804 rend)
8349 fetches (92.5%) have at least 25 non-zero cells on both circuits (8419 general and 8670 rend)
8285 fetches (91.8%) have at least 30 non-zero cells on both circuits (8392 general and 8615 rend)
8231 fetches (91.2%) have at least 31 non-zero cells on both circuits (8380 general and 8554 rend)
7255 fetches (80.4%) have at least 32 non-zero cells on both circuits (8346 general and 7523 rend)
6226 fetches (69.0%) have at least 33 non-zero cells on both circuits (8304 general and 6460 rend)
6034 fetches (66.8%) have at least 34 non-zero cells on both circuits (8231 general and 6166 rend)
5876 fetches (65.1%) have at least 35 non-zero cells on both circuits (8127 general and 5992 rend)
5109 fetches (56.6%) have at least 40 non-zero cells on both circuits (6975 general and 5550 rend)
4938 fetches (54.7%) have at least 45 non-zero cells on both circuits (6624 general and 5161 rend)
4869 fetches (53.9%) have at least 50 non-zero cells on both circuits (6329 general and 5090 rend)
4598 fetches (50.9%) have at least 75 non-zero cells on both circuits (5910 general and 4837 rend)
4393 fetches (48.7%) have at least 100 non-zero cells on both circuits (5638 general and 4630 rend)
3803 fetches (42.1%) have at least 200 non-zero cells on both circuits (4958 general and 4072 rend)
3534 fetches (39.1%) have at least 300 non-zero cells on both circuits (4552 general and 3831 rend)
3280 fetches (36.3%) have at least 400 non-zero cells on both circuits (4292 general and 3575 rend)
3044 fetches (33.7%) have at least 500 non-zero cells on both circuits (4007 general and 3347 rend)
3001 fetches (33.2%) have at least 512 non-zero cells on both circuits (3977 general and 3316 rend)

Dataset curl
Processing 2000 files...

################### stats for dataset curl ###################

2000 fetches using 3994 circuits for 2000 tags/websites
2000 circuits were directory circuits
9 fetches had no general circuits
2000 fetches had no rend circuits
0 fetches had rend circuits larger than general circuits and both were below 100
0 fetches had rend circuits larger than general circuits
0 fetches had general circuits larger than rend circuits
Average number of rend circuits per fetch: 0.00 (median: 0, min: 0, max: 0)
0 fetches had the largest rend circuit as cloudflare
1 circuits were filtered out due to domain in [b'securedrop.org', b'185.220.103.112', b'185.220.103.119']
Common domains in all fetches: [b'185.220.103.112']
Top-20 most common domains:
b'193.10.226.38': 1991
b'185.220.103.112': 1000
b'185.220.103.119': 1000
0 fetches (0.0%) have at least 10 non-zero cells on both circuits (0 general and 0 rend)
0 fetches (0.0%) have at least 25 non-zero cells on both circuits (0 general and 0 rend)
0 fetches (0.0%) have at least 30 non-zero cells on both circuits (0 general and 0 rend)
0 fetches (0.0%) have at least 31 non-zero cells on both circuits (0 general and 0 rend)
0 fetches (0.0%) have at least 32 non-zero cells on both circuits (0 general and 0 rend)
0 fetches (0.0%) have at least 33 non-zero cells on both circuits (0 general and 0 rend)
0 fetches (0.0%) have at least 34 non-zero cells on both circuits (0 general and 0 rend)
0 fetches (0.0%) have at least 35 non-zero cells on both circuits (0 general and 0 rend)
0 fetches (0.0%) have at least 40 non-zero cells on both circuits (0 general and 0 rend)
0 fetches (0.0%) have at least 45 non-zero cells on both circuits (0 general and 0 rend)
0 fetches (0.0%) have at least 50 non-zero cells on both circuits (0 general and 0 rend)
0 fetches (0.0%) have at least 75 non-zero cells on both circuits (0 general and 0 rend)
0 fetches (0.0%) have at least 100 non-zero cells on both circuits (0 general and 0 rend)
0 fetches (0.0%) have at least 200 non-zero cells on both circuits (0 general and 0 rend)
0 fetches (0.0%) have at least 300 non-zero cells on both circuits (0 general and 0 rend)
0 fetches (0.0%) have at least 400 non-zero cells on both circuits (0 general and 0 rend)
0 fetches (0.0%) have at least 500 non-zero cells on both circuits (0 general and 0 rend)
0 fetches (0.0%) have at least 512 non-zero cells on both circuits (0 general and 0 rend)

```

### Circuit fingerprinting

Run `./analysis/extract-cf.py` to extract classes for Circuit Fingerprinting if
you did not download them above.

Below, we run binary classification using [Deep
Fingerprinting](https://github.com/deep-fingerprinting/df/), showing that each
circuit kind (general, hsdir, intro, and rend) are classifiable with 99.9%
accuracy and a FPR below 0.1% (key takeaway from Section 5.1).

Keep in mind that all classification tasks use randomness so some minor
differences are expected (note to self: use static seeds in future work).

```bash
./binary-classify.py clearnet-only-general.npz clearnet-no-general.npz -l 512
05:36:45 loading datasets done, 52700 samples, 21795 from clearnet-only-general.npz, 30905 from clearnet-no-general.npz
05:36:45 baseline accuracy 0.5864
05:36:45 using DF with 512 cells
05:36:45 training with 200 epochs, batch size 128, patience 10
05:36:45 using NVIDIA GeForce RTX 3090
05:36:45 we do 10-fold cross validation with a 8:1:1 split
06:30:42 done, 10-fold cross validation results
06:30:42 accuracy mean: 0.9994, std: 0.0002
06:30:42 fpr mean: 0.0002, std: 0.0003
```

```bash
./binary-classify.py onion-only-hsdir.npz onion-no-hsdir.npz -l 512
06:30:44 loading datasets done, 72814 samples, 24491 from onion-only-hsdir.npz, 48323 from onion-no-hsdir.npz
06:30:44 baseline accuracy 0.6636
06:30:44 using DF with 512 cells
06:30:44 training with 200 epochs, batch size 128, patience 10
06:30:44 using NVIDIA GeForce RTX 3090
06:30:44 we do 10-fold cross validation with a 8:1:1 split
07:42:33 done, 10-fold cross validation results
07:42:33 accuracy mean: 0.9991, std: 0.0003
07:42:33 fpr mean: 0.0011, std: 0.0004
```

```bash
./binary-classify.py onion-only-intro.npz onion-no-intro.npz -l 512
07:42:35 loading datasets done, 72814 samples, 18592 from onion-only-intro.npz, 54222 from onion-no-intro.npz
07:42:35 baseline accuracy 0.7447
07:42:35 using DF with 512 cells
07:42:35 training with 200 epochs, batch size 128, patience 10
07:42:35 using NVIDIA GeForce RTX 3090
07:42:35 we do 10-fold cross validation with a 8:1:1 split
08:45:30 done, 10-fold cross validation results
08:45:30 accuracy mean: 0.9995, std: 0.0002
08:45:30 fpr mean: 0.0002, std: 0.0002
```

```bash
./binary-classify.py onion-only-rend.npz onion-no-rend.npz -l 512
08:45:33 loading datasets done, 72814 samples, 18400 from onion-only-rend.npz, 54414 from onion-no-rend.npz
08:45:33 baseline accuracy 0.7473
08:45:33 using DF with 512 cells
08:45:33 training with 200 epochs, batch size 128, patience 10
08:45:33 using NVIDIA GeForce RTX 3090
08:45:33 we do 10-fold cross validation with a 8:1:1 split
09:37:36 done, 10-fold cross validation results
09:37:36 accuracy mean: 0.9994, std: 0.0003
09:37:36 fpr mean: 0.0002, std: 0.0002
```

### Automatic Onion-Location Fingerprinting

Run `./analysis/extract-ol.py` to extract classes for onion location
fingerprinting if you did not download them above.

Below you find the initial results from the start of Section 5.2.2, showing that
automatic onion-location is highly fingerprintable.

```bash
./binary-classify.py autoloc-100.npz clearnet-ol-0.npz
00:41:47 loading datasets done, 18535 samples, 4392 from autoloc-100.npz, 14143 from clearnet-ol-0.npz
00:41:47 baseline accuracy 0.7630
00:41:47 using DF with 5000 cells
00:41:47 training with 200 epochs, batch size 128, patience 10
00:41:47 using NVIDIA GeForce RTX 3090
00:41:47 we do 10-fold cross validation with a 8:1:1 split
00:57:09 done, 10-fold cross validation results
00:57:09 accuracy mean: 0.9985, std: 0.0010
00:57:09 fpr mean: 0.0018, std: 0.0015
```

```bash
./binary-classify.py autoloc-100.npz onion-ol-0.npz
00:57:12 loading datasets done, 9077 samples, 4392 from autoloc-100.npz, 4685 from onion-ol-0.npz
00:57:12 baseline accuracy 0.5161
00:57:12 using DF with 5000 cells
00:57:12 training with 200 epochs, batch size 128, patience 10
00:57:12 using NVIDIA GeForce RTX 3090
00:57:12 we do 10-fold cross validation with a 8:1:1 split
01:08:24 done, 10-fold cross validation results
01:08:24 accuracy mean: 0.9898, std: 0.0040
01:08:24 fpr mean: 0.0127, std: 0.0076
```

### Open-world experiments

As part of validating that Onion-Location Fingerprinting is robust against
unknown Onion-Location sites, we ran an open-world experiment in the middle of
Section 5.2.2.

```bash
./binary-classify.py autoloc-100.npz clearnet-ol-0.npz --open-world 0.8
01:29:28 loading datasets done, 18535 samples, 4392 from autoloc-100.npz, 14143 from clearnet-ol-0.npz
01:29:28 baseline accuracy 0.7630
01:29:28 using DF with 5000 cells
01:29:28 'OPEN WORLD' MODE: splitting by tag, training probability 0.8
01:29:28 training with 200 epochs, batch size 128, patience 10
01:29:28 using NVIDIA GeForce RTX 3090
01:29:28 we do 10-fold cross validation with a 8:1:1 split
01:49:30 done, 10-fold cross validation results
01:49:30 accuracy mean: 0.9972, std: 0.0015
01:49:30 fpr mean: 0.0023, std: 0.0011
```

```bash
./binary-classify.py autoloc-100.npz onion-ol-0.npz --open-world 0.8
01:49:33 loading datasets done, 9077 samples, 4392 from autoloc-100.npz, 4685 from onion-ol-0.npz
01:49:33 baseline accuracy 0.5161
01:49:33 using DF with 5000 cells
01:49:33 'OPEN WORLD' MODE: splitting by tag, training probability 0.8
01:49:33 training with 200 epochs, batch size 128, patience 10
01:49:33 using NVIDIA GeForce RTX 3090
01:49:33 we do 10-fold cross validation with a 8:1:1 split
02:00:15 done, 10-fold cross validation results
02:00:15 accuracy mean: 0.9776, std: 0.0043
02:00:15 fpr mean: 0.0296, std: 0.0105
```

```bash
./binary-classify.py autoloc-100.npz clearnet-ol-0.npz --open-world 0.5
02:00:19 loading datasets done, 18535 samples, 4392 from autoloc-100.npz, 14143 from clearnet-ol-0.npz
02:00:19 baseline accuracy 0.7630
02:00:19 using DF with 5000 cells
02:00:19 'OPEN WORLD' MODE: splitting by tag, training probability 0.5
02:00:19 training with 200 epochs, batch size 128, patience 10
02:00:19 using NVIDIA GeForce RTX 3090
02:00:19 we do 10-fold cross validation with a 8:1:1 split
02:11:49 done, 10-fold cross validation results
02:11:49 accuracy mean: 0.9974, std: 0.0009
02:11:49 fpr mean: 0.0026, std: 0.0012
```

```bash
./binary-classify.py autoloc-100.npz onion-ol-0.npz --open-world 0.5
02:11:52 loading datasets done, 9077 samples, 4392 from autoloc-100.npz, 4685 from onion-ol-0.npz
02:11:52 baseline accuracy 0.5161
02:11:52 using DF with 5000 cells
02:11:52 'OPEN WORLD' MODE: splitting by tag, training probability 0.5
02:11:52 training with 200 epochs, batch size 128, patience 10
02:11:53 using NVIDIA GeForce RTX 3090
02:11:53 we do 10-fold cross validation with a 8:1:1 split
02:19:16 done, 10-fold cross validation results
02:19:16 accuracy mean: 0.9705, std: 0.0043
02:19:16 fpr mean: 0.0415, std: 0.0064
```

```bash
./binary-classify.py autoloc-100.npz clearnet-ol-0.npz --open-world 0.3
02:19:18 loading datasets done, 18535 samples, 4392 from autoloc-100.npz, 14143 from clearnet-ol-0.npz
02:19:18 baseline accuracy 0.7630
02:19:18 using DF with 5000 cells
02:19:18 'OPEN WORLD' MODE: splitting by tag, training probability 0.3
02:19:18 training with 200 epochs, batch size 128, patience 10
02:19:18 using NVIDIA GeForce RTX 3090
02:19:18 we do 10-fold cross validation with a 8:1:1 split
02:25:10 done, 10-fold cross validation results
02:25:10 accuracy mean: 0.9965, std: 0.0011
02:25:10 fpr mean: 0.0028, std: 0.0009
```

```bash
./binary-classify.py autoloc-100.npz onion-ol-0.npz --open-world 0.3
02:25:11 loading datasets done, 9077 samples, 4392 from autoloc-100.npz, 4685 from onion-ol-0.npz
02:25:11 baseline accuracy 0.5161
02:25:11 using DF with 5000 cells
02:25:11 'OPEN WORLD' MODE: splitting by tag, training probability 0.3
02:25:11 training with 200 epochs, batch size 128, patience 10
02:25:11 using NVIDIA GeForce RTX 3090
02:25:11 we do 10-fold cross validation with a 8:1:1 split
02:28:14 done, 10-fold cross validation results
02:28:14 accuracy mean: 0.9627, std: 0.0025
02:28:14 fpr mean: 0.0484, std: 0.0091
```

### Positive class limit

Next, still in Section 5.2.2, we evaluated the impact of the minimum size of the
positive class.

```bash
./binary-classify.py autoloc-75.npz clearnet-ol-0.npz
02:47:45 loading datasets done, 18740 samples, 4597 from autoloc-75.npz, 14143 from clearnet-ol-0.npz
02:47:45 baseline accuracy 0.7547
02:47:45 using DF with 5000 cells
02:47:45 training with 200 epochs, batch size 128, patience 10
02:47:45 using NVIDIA GeForce RTX 3090
02:47:45 we do 10-fold cross validation with a 8:1:1 split
03:06:23 done, 10-fold cross validation results
03:06:23 accuracy mean: 0.9987, std: 0.0006
03:06:23 fpr mean: 0.0013, std: 0.0010
```

```bash
./binary-classify.py autoloc-50.npz clearnet-ol-0.npz
03:06:25 loading datasets done, 19012 samples, 4869 from autoloc-50.npz, 14143 from clearnet-ol-0.npz
03:06:25 baseline accuracy 0.7439
03:06:25 using DF with 5000 cells
03:06:25 training with 200 epochs, batch size 128, patience 10
03:06:25 using NVIDIA GeForce RTX 3090
03:06:25 we do 10-fold cross validation with a 8:1:1 split
03:24:45 done, 10-fold cross validation results
03:24:45 accuracy mean: 0.9983, std: 0.0009
03:24:45 fpr mean: 0.0009, std: 0.0009
```

```bash
./binary-classify.py autoloc-35.npz clearnet-ol-0.npz
03:24:47 loading datasets done, 19949 samples, 5806 from autoloc-35.npz, 14143 from clearnet-ol-0.npz
03:24:47 baseline accuracy 0.7090
03:24:47 using DF with 5000 cells
03:24:47 training with 200 epochs, batch size 128, patience 10
03:24:47 using NVIDIA GeForce RTX 3090
03:24:47 we do 10-fold cross validation with a 8:1:1 split
04:05:02 done, 10-fold cross validation results
04:05:02 accuracy mean: 0.9854, std: 0.0024
04:05:02 fpr mean: 0.0052, std: 0.0017
```

```bash
./binary-classify.py autoloc-30.npz clearnet-ol-0.npz
04:05:04 loading datasets done, 20846 samples, 6703 from autoloc-30.npz, 14143 from clearnet-ol-0.npz
04:05:04 baseline accuracy 0.6785
04:05:04 using DF with 5000 cells
04:05:04 training with 200 epochs, batch size 128, patience 10
04:05:04 using NVIDIA GeForce RTX 3090
04:05:04 we do 10-fold cross validation with a 8:1:1 split
04:45:18 done, 10-fold cross validation results
04:45:18 accuracy mean: 0.9809, std: 0.0025
04:45:18 fpr mean: 0.0061, std: 0.0027
```

```bash
./binary-classify.py autoloc-75.npz onion-ol-0.npz
04:45:20 loading datasets done, 9282 samples, 4597 from autoloc-75.npz, 4685 from onion-ol-0.npz
04:45:20 baseline accuracy 0.5047
04:45:20 using DF with 5000 cells
04:45:20 training with 200 epochs, batch size 128, patience 10
04:45:20 using NVIDIA GeForce RTX 3090
04:45:20 we do 10-fold cross validation with a 8:1:1 split
04:56:01 done, 10-fold cross validation results
04:56:01 accuracy mean: 0.9847, std: 0.0039
04:56:01 fpr mean: 0.0177, std: 0.0106
```

```bash
./binary-classify.py autoloc-50.npz onion-ol-0.npz
04:56:03 loading datasets done, 9554 samples, 4869 from autoloc-50.npz, 4685 from onion-ol-0.npz
04:56:03 baseline accuracy 0.5096
04:56:03 using DF with 5000 cells
04:56:03 training with 200 epochs, batch size 128, patience 10
04:56:03 using NVIDIA GeForce RTX 3090
04:56:03 we do 10-fold cross validation with a 8:1:1 split
05:08:18 done, 10-fold cross validation results
05:08:18 accuracy mean: 0.9831, std: 0.0046
05:08:18 fpr mean: 0.0166, std: 0.0072
```

```bash
./binary-classify.py autoloc-35.npz onion-ol-0.npz
05:08:19 loading datasets done, 10491 samples, 5806 from autoloc-35.npz, 4685 from onion-ol-0.npz
05:08:19 baseline accuracy 0.5534
05:08:19 using DF with 5000 cells
05:08:19 training with 200 epochs, batch size 128, patience 10
05:08:19 using NVIDIA GeForce RTX 3090
05:08:19 we do 10-fold cross validation with a 8:1:1 split
05:21:27 done, 10-fold cross validation results
05:21:27 accuracy mean: 0.9852, std: 0.0039
05:21:27 fpr mean: 0.0192, std: 0.0099
```

```bash
./binary-classify.py autoloc-30.npz onion-ol-0.npz
05:21:28 loading datasets done, 11388 samples, 6703 from autoloc-30.npz, 4685 from onion-ol-0.npz
05:21:28 baseline accuracy 0.5886
05:21:28 using DF with 5000 cells
05:21:28 training with 200 epochs, batch size 128, patience 10
05:21:28 using NVIDIA GeForce RTX 3090
05:21:28 we do 10-fold cross validation with a 8:1:1 split
05:36:43 done, 10-fold cross validation results
05:36:43 accuracy mean: 0.9874, std: 0.0032
05:36:43 fpr mean: 0.0178, std: 0.0073
```

### Overlap utility

To show that the overlap between circuit contents is informative, we created an
artificial negative dataset in the end of Section 5.2.2.

```bash
./binary-classify.py autoloc-100.npz negative-ol-100.npz
02:28:15 loading datasets done, 9789 samples, 4392 from autoloc-100.npz, 5397 from negative-ol-100.npz
02:28:15 baseline accuracy 0.5513
02:28:15 using DF with 5000 cells
02:28:15 training with 200 epochs, batch size 128, patience 10
02:28:15 using NVIDIA GeForce RTX 3090
02:28:15 we do 10-fold cross validation with a 8:1:1 split
02:47:43 done, 10-fold cross validation results
02:47:43 accuracy mean: 0.9136, std: 0.0108
02:47:43 fpr mean: 0.0980, std: 0.0149
```

### Onion-Location via Sauteed Onions using TLS handshake ("curl")

The curl results used in Section 5.2.4. Note the two extra samples for curl here
than in the paper. A small imperfection. We refactored (cleaned up research
grade code!) for the artifact review. Probably something small changed. Keeping
it here for sake of transparency (has no impact on conclusions).

```bash
./binary-classify.py curl-only-general.npz clearnet-only-general.npz
01:08:27 loading datasets done, 23788 samples, 1993 from curl-only-general.npz, 21795 from clearnet-only-general.npz
01:08:27 baseline accuracy 0.9162
01:08:27 using DF with 5000 cells
01:08:27 training with 200 epochs, batch size 128, patience 10
01:08:27 using NVIDIA GeForce RTX 3090
01:08:27 we do 10-fold cross validation with a 8:1:1 split
01:29:24 done, 10-fold cross validation results
01:29:24 accuracy mean: 0.9998, std: 0.0003
01:29:24 fpr mean: 0.0000, std: 0.0001
```
