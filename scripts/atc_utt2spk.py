# Generates the utt2spk file for the ATC data.
# Can only be run after atc_text.py has generated text files.

import os, re, sys
from os.path import join as pjoin

"""

Usage:
    python atc_utt2spk.py <UFA-directory> <ATCOSIM-directory> <data_path>

"""

def make_utt2spk_line(utt, speaker):
    return " ".join([utt, speaker + "\n"])

def main(ufa_dir, atcosim_dir, data_path):
    train_path = pjoin(data_path, "atc")
    test_path = pjoin(data_path, "test")
    
    # Creates the utt2spk files.
    train_utt2spk = open(pjoin(train_path, "utt2spk"), "w")
    test_utt2spk = open(pjoin(test_path, "utt2spk"), "w")

    # Uses the 'text' files to create the 'utt2spk' files
    train_text = open(pjoin(train_path, "text"), "r")
    test_text = open(pjoin(test_path, "text"), "r")

    # Writes the utt2spk files following this format:
    #       utt_id speaker_id
    for line in train_text:
        words = line.split()
        if words[0].startswith("de"):
            speaker = words[0].split("-")[0]
            train_utt2spk.write(make_utt2spk_line(words[0], speaker))
        else:
            speaker = words[0].split("_")[0]
            train_utt2spk.write(make_utt2spk_line(words[0], speaker))

    for line in test_text:
        words = line.split()
        speaker = words[0].split("-")[0]
        test_utt2spk.write(make_utt2spk_line(words[0], speaker))
        
if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
