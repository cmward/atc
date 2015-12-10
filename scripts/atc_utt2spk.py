# Generates the utt2spk file for the ATC data.
# Can only be run after atc_text.py has genereated text files.

import os, re
from os.path import join as pjoin

PROJECT_ROOT = '/home/matrick/Desktop/ATCProject'
UFA = pjoin(PROJECT_ROOT, 'corpora/UFA_DE')
ATCOSIM = pjoin(PROJECT_ROOT, 'corpora/ATCOSIM')
PARTITIONS = pjoin(PROJECT_ROOT, 'data_partitioning')

train_path = "data/train/atc_tmp"
test_path = "data/test/atc_tmp"

# Create temporary utt2spk files.
train_utt2spk = open(pjoin(train_path, "utt2spk"), "w")
test_utt2spk = open(pjoin(test_path, "utt2spk"), "w")

# Uses the 'text' files to create the 'utt2spk' files
train_text = open(pjoin(train_path, "text"), "r")
test_text = open(pjoin(test_path, "text"), "r")
lines = []

# Writes the utt2spk files following this format:
#       utt_id speaker_id
for line in train_text:
    words = line.split()
    if words[0].startswith("de"):
        speaker = words[0].split("-")[0]
        train_utt2spk.write(" ".join([words[0], speaker + "\n"]))
    else:
        speaker = words[0].split("_")[0]
        train_utt2spk.write(" ".join([words[0], speaker + "\n"]))

for line in test_text:
    words = line.split()
    speaker = words[0].split("-")[0]
    test_utt2spk.write(" ".join([words[0], speaker + "\n"]))
