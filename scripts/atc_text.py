# Generates the text files for the ATC data.
# This should be run before other the other scripts that generate files for Kaldi.

import os, re, sys
from os.path import join as pjoin
from normalize_text import *

"""

Usage:
    python atc_text.py <UFA-directory> <ATCOSIM-directory> <data_path>    

"""

def make_text_line(utt_id, line):
    return " ".join([utt_id, line + "\n"])

def add_atcosim_text(speakers, atcosim_dir, train_text):
    for speaker in speakers:
        speaker_dir = pjoin(atcosim_dir, "TXTdata", speaker)
        subdirs = os.listdir(speaker_dir)
        for subpath in subdirs:
            transcripts = os.listdir(pjoin(speaker_dir, subpath))
            for t in transcripts:
                utt_id = t[:-4]
                transcript_file = open(pjoin(speaker_dir, subpath, t))
                line = normalize_atcosim(transcript_file.read(), word_map)
                train_text.write(make_text_line(utt_id, line))


def add_ufa_text(ufa_dir, train_text, test_text):
    ufa_transcript = open(pjoin(ufa_dir, "trans/UFA_DE-test.trans"))
    counter = 0
    for line in ufa_transcript:
        # The first 4034 utterances are all test data.
        words = normalize_ufa(line).split()
        utt_id = words[-1][1:-1]
        if counter < 4034:
            test_text.write(make_text_line(utt_id, " ".join(words[:-1])))
            counter += 1
        else:
            train_text.write(make_text_line(utt_id, " ".join(words[:-1])))

def main(ufa_dir, atcosim_dir, data_path):
    train_path = pjoin(data_path, "atc")
    test_path = pjoin(data_path, "test")
    # Makes the directories if they don't exist.
    if not os.path.exists(train_path):
        os.makedirs(train_path)
    if not os.path.exists(test_path):
        os.makedirs(test_path)
    
    # Creates the 'text' files
    train_text = open(pjoin(train_path, "text"), "w")
    test_text =  open(pjoin(test_path, "text"), "w")

    ## Add ATCOSIM text.
    # List of German speakers in ATCOSIM.
    speakers = ["sm1", "sm2", "sm3", "sm4"]
    add_atcosim_text(speakers, atcosim_dir, train_text)

    ## Add UFA text.
    add_ufa_text(ufa_dir, train_text, test_text)
    
if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
