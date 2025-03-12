# Artifact Appendix

Paper title: Onion-Location Measurements and Fingerprinting

Artifacts HotCRP Id: https://artifact.petsymposium.org/artifact2025.3/paper.php/15

Requested Badge: **Available**

## Description

This artifact makes the two open-source tools and collected datasets available
(Section 4) and shows how to use this as input for the analysis in (Section 5).

See [README](./README.md) for a complete description of this artifact.  The
remainder of this document provides further context relating to Section 5.

### Security/Privacy Issues and Ethical Concerns (All badges)

No risk to the reviewer's machine.

No ethical concerns with the artifacts.

## Basic Requirements (Only for Functional and Reproduced badges)

GPU able to run Pytorch. About 45 GiB of disk. Compute time about a day.

### Hardware Requirements

No specific requirements (we're only requesting the **Available** badge, in part
because of the limitation mentioned below and also because the data collection
at large is compute heavy and requires around one month of calendar time).

### Software Requirement

Should work on Windows and Linux, nothing special. Detailed in the README.md.

### Estimated Time and Storage Consumption

Storage in total about 45 GiB. The evaluation involves two steps:

1. Download and process the dataset. This takes around 8-10 hours. If the
   Python-scripts start running they will finish eventually, nothing special
   happens mid-way or so.

2. Classification using Pytorch. If you hit the training loop in the first run
   of the classification script you're good. The classification involves running
   the same script on different parts of the dataset. Running time depends on
   your GPU, on a RTX 3090 it took about 9 hours.

## Environment

Clone this repo and follow the README.md. Basically a Python environment with
one pip install and you're good to go. Dataset downloads have checksums.

There is a helpful `run.sh` script for the data analysis part and a transcript
of a run to compare with.

### Accessibility (All badges)

Available here: <https://github.com/pylls/ol-measurements-and-fp>.

We host the datasets on an institutional webserver.

Please evaluate the main branch. We will not update or change the repository
during the evaluation except on your request.

### Set up the environment (Only for Functional and Reproduced badges)

```bash
git clone git@github.com:pylls/ol-measurements-and-fp.git
```

Further steps are in the README.md file in great detail.

### Testing the Environment (Only for Functional and Reproduced badges)

Download the data and process it per the README. Afterwards, if the following
run gives results for fold 0 (should take a couple of minutes with a GPU only),
you're good:

```bash
./binary-classify.py autoloc-100.npz clearnet-ol-0.npz
```

## Artifact Evaluation (Only for Functional and Reproduced badges)

We directly map results and experiments in the README. Below each is summarized.

### Main Results and Claims

#### Main Result 1: Total circuits count in Table 2

Table 2 in the paper lists different circuit counts for our four datasets. The
dataset stats script confirms the total circuit counts for the 1505 websites.

#### Main Result 2: Circuit Fingerprinting accuracy

The Circuit Fingerprinting section underpins our key takeaway from Section 5.1
in the paper: circuit kind (general, hsdir, intro, and rend) are classifiable
with 99.9% accuracy and a FPR below 0.1%.

#### Main Result 3: Automatic Onion-Location Fingerprinting accuracy

From Section 5.2.2, the binary classifications show about 99% accuracy and a low
1% FPR.

#### Main Result 4: Open-world experiments

From the middle of Section 5.2.2, we validate that Onion-Location Fingerprinting
is robust against unknown Onion-Location sites by showing a small decrease with
significant changes in world ratios. Recall that we are in a ~closed world by
default due to onion-location sites being enumerable, and the excessive
filtering for the onion negative class dataset.

#### Main Result 5: Positive class limit

From Section 5.2.2, the impact of the attacker reducing the minimum size of the
positive class is not significant (albeit self-defeating as noted in the paper).

#### Main Result 6: Overlap utility

At the end of Section 5.2.2, we show that the overlap between circuits is highly
informative on its own.

## Limitations (Only for Functional and Reproduced badges)

The dataset that is analyzed in Section 5 requires a modified version of Tor to
be collected.  For safety reasons, we are not publishing the modified version of
Tor.  The paper provides further ethical considerations.

## Notes on Reusability (Only for Functional and Reproduced badges)

Only the above limitation, everything else is available and usable.
