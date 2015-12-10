# Generates the segments file for a given pizza data set.
# Can only be run after atc_wavscp.py has generated wav.scp files.

import os, re, subprocess, wave
from os.path import join as pjoin

PROJECT_ROOT = '/home/matrick/Desktop/ATCProject'
UFA = pjoin(PROJECT_ROOT, 'corpora/UFA_DE')
ATCOSIM = pjoin(PROJECT_ROOT, 'corpora/ATCOSIM')

train_path = "data/train/atc_tmp"
test_path = "data/test/atc_tmp"

# The temporary wav.scp files are used to make the segments files.
train_wavscp = open(pjoin(train_path, "wav.scp"), "r")
test_wavscp = open(pjoin(test_path, "wav.scp"), "r")

# Create temporary segments files.
train_segments = open(pjoin(train_path, "segments"), "w")
test_segments = open(pjoin(test_path, "segments"), "w")

# Create temporary reco2file_and_channel files.
train_reco = open(pjoin(train_path, "reco2file_and_channel"), "w")
test_reco = open(pjoin(test_path, "reco2file_and_channel"), "w")

# Writes the file in the following format:
#
# utt_id rec_id start_time end_time
#
# In this case utt_id and rec_id are the same.

for line in train_wavscp:
    parts = line.split()
    wav = wave.open(parts[1])
    length = str(round(((1.0 * wav.getnframes ()) / wav.getframerate ()) - 0.01, 2))
    train_segments.write(" ".join([parts[0], parts[0], "0.00", length + "\n"]))
    train_reco.write(" ".join([parts[0], parts[0], "A\n"]))
    
for line in test_wavscp:
    parts = line.split()
    wav = wave.open(parts[1])
    length = str(round(((1.0 * wav.getnframes ()) / wav.getframerate ()) - 0.01, 2))
    test_segments.write(" ".join([parts[0], parts[0], "0.00", length + "\n"]))
    test_reco.write(" ".join([parts[0], parts[0], "A\n"]))
