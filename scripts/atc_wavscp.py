# Generates the wav.scp files for the ATC data.

import os, re, sys
from os.path import join as pjoin

"""

Usage:
    python atc_wavscp.py <UFA-audio-dir> <ATCOSIM-audio-dir> <data-partitioning-dir> <data_path>

"""

def make_wavscp_line(utt_id, wav_path):
    return " ".join([utt_id, wav_path + "\n"])

def add_atcosim_lines(atcosim_audio_dir, speakers, wavscp_file):
    for speaker in speakers:
        speaker_dir = pjoin(atcosim_audio_dir, speaker)
        subdirs = os.listdir(speaker_dir)
        for sub in subdirs:
            wav_files = os.listdir(pjoin(speaker_dir, sub))
            for wav in wav_files:
                utt_id = wav[:-4]
                wavscp_file.write(make_wavscp_line(utt_id, pjoin(speaker_dir, sub, wav)))

def add_ufa_lines(ufa_audio_dir, speakers, wavscp_file):
    for speaker in speakers:
        # This dir should be wherever you put your fixed wav files.
        speaker_dir = pjoin(ufa_audio_dir, speaker)
        wav_files = os.listdir(speaker_dir)
        for wav in wav_files:
            utt_id = wav[:-4]
            wavscp_file.write(make_wavscp_line(utt_id, pjoin(speaker_dir, wav)))

def main(ufa_audio_dir, atcosim_audio_dir, partitions, data_path):
    atcosim_train_spkrs = ["sm1", "sm2", "sm3", "sm4"]
    ufa_train_spkrs = [spkr.strip() for spkr in open(pjoin(partitions, "ufa_train_speakers"))]
    ufa_test_spkrs = [spkr.strip() for spkr in open(pjoin(partitions, "ufa_test_speakers"))]
    train_path = pjoin(data_path, "atc")
    test_path = pjoin(data_path, "test")

    # Creates the wav.scp files.
    train_wavscp = open(pjoin(train_path, "wav.scp"), "w")
    test_wavscp = open(pjoin(test_path, "wav.scp"), "w")

    add_atcosim_lines(atcosim_audio_dir, atcosim_train_spkrs, train_wavscp)
    add_ufa_lines(ufa_audio_dir, ufa_train_spkrs, train_wavscp)
    add_ufa_lines(ufa_audio_dir, ufa_test_spkrs, test_wavscp)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
