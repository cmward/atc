# Generates the segments file for a given pizza data set.
# Can only be run after atc_wavscp.py has generated wav.scp files.

import os, re, sys, wave
from os.path import join as pjoin

"""

Usage:
    python atc_segments_and_reco.py <data-path>

"""

def wav_length(wav_path):
    wav = wave.open(wav_path)
    length = str(round(((1.0 * wav.getnframes ()) / wav.getframerate ()) - 0.01, 2))
    return length

def make_segments_line(rec_id, length):
    return " ".join([rec_id, rec_id, "0.00", length + "\n"])

def make_reco_line(rec_id):
    return " ".join([rec_id, rec_id, "A\n"])

def add_lines_to_files(wavscp_file, segments_file, reco_file):
    for line in wavscp_file:
        parts = line.split()
        length = wav_length(parts[1])
        segments_file.write(make_segments_line(parts[0], length))
        reco_file.write(make_reco_line(parts[0]))

def main(data_path):
    train_path = pjoin(data_path, "atc")
    test_path = test_path = pjoin(data_path, "test")

    # The wav.scp files are used to make the segments files.
    train_wavscp = open(pjoin(train_path, "wav.scp"), "r")
    test_wavscp = open(pjoin(test_path, "wav.scp"), "r")

    # Creates the segments files.
    train_segments = open(pjoin(train_path, "segments"), "w")
    test_segments = open(pjoin(test_path, "segments"), "w")

    # Creates the reco2file_and_channel files.
    train_reco = open(pjoin(train_path, "reco2file_and_channel"), "w")
    test_reco = open(pjoin(test_path, "reco2file_and_channel"), "w")

    # Writes the segments file in the following format:
    #
    # utt_id rec_id start_time end_time
    #
    # In this case utt_id and rec_id are the same.

    add_lines_to_files(train_wavscp, train_segments, train_reco)
    add_lines_to_files(test_wavscp, test_segments, test_reco)

if __name__ == "__main__":
    main(sys.argv[1])
