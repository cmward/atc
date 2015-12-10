# Generates the text files for the ATC data.
# This should be run before other the other scripts that generate files for Kaldi.

import os, re
from os.path import join as pjoin
from normalize_text import *

PROJECT_ROOT = '/home/matrick/Desktop/ATCProject'
UFA = pjoin(PROJECT_ROOT, 'corpora/UFA_DE')
ATCOSIM = pjoin(PROJECT_ROOT, 'corpora/ATCOSIM')

# Makes the temp directories if they don't exist.
train_path = "data/train/atc_tmp"
test_path = "data/test/atc_tmp"

if not os.path.exists(train_path):
    os.makedirs(train_path)
if not os.path.exists(test_path):
    os.makedirs(test_path)
    
# Creates the 'text' file
train_text = open(pjoin(train_path, "text"), "w")
test_text =  open(pjoin(test_path, "text"), "w")

## Write ATCOSIM text.

# List of German speakers in ATCOMSIM.
speakers = ["sm1", "sm2", "sm3", "sm4"]

for speaker in speakers:
    speaker_dir = pjoin(ATCOSIM, "TXTdata", speaker)
    subdirs = os.listdir(speaker_dir)
    for subpath in subdirs:
        transcripts = os.listdir(pjoin(speaker_dir, subpath))
        for t in transcripts:
            utt_id = t[:-4]
            transcript_file = open(pjoin(speaker_dir, subpath, t))
            line = normalize_atcosim(transcript_file.read(), word_map)
            train_text.write(" ".join([utt_id, line + "\n"]))

## Write UFA text.

ufa_transcript = open(pjoin(UFA, "trans/UFA_DE-test.trans"))
counter = 0
for line in ufa_transcript:
    # The first 4034 utterances are all test data.
    words = normalize_ufa(line).split()
    utt_id = words[-1][1:-1]
    if counter < 4034:
        test_text.write(utt_id + " " + " ".join(words[:-1]) + "\n")
        counter += 1
    else:
        train_text.write(utt_id + " " + " ".join(words[:-1])+ "\n")
        
        

