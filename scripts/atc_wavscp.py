# Generates the wav.scp files for the ATC data.

import os, re
from os.path import join as pjoin

PROJECT_ROOT = '/home/matrick/Desktop/ATCProject'
UFA = pjoin(PROJECT_ROOT, 'corpora/UFA_DE')
ATCOSIM = pjoin(PROJECT_ROOT, 'corpora/ATCOSIM')
PARTITIONS = pjoin(PROJECT_ROOT, 'data_partitioning')

atcosim_train_spkrs = ["sm1", "sm2", "sm3", "sm4"]
ufa_train_spkrs = [spkr.strip() for spkr in open(pjoin(PARTITIONS, "ufa_train_speakers"))]
ufa_test_spkrs = [spkr.strip() for spkr in open(pjoin(PARTITIONS, "ufa_test_speakers"))]

train_path = "data/train/atc_tmp"
test_path = "data/test/atc_tmp"

train_wavscp = open(pjoin(train_path, "wav.scp"), "w")
test_wavscp = open(pjoin(test_path, "wav.scp"), "w")

for speaker in atcosim_train_spkrs:
    speaker_dir = pjoin(ATCOSIM, "WAVdata", speaker)
    subdirs = os.listdir(speaker_dir)
    for sub in subdirs:
        wav_files = os.listdir(pjoin(speaker_dir, sub))
        for wav in wav_files:
            utt_id = wav[:-4]
            train_wavscp.write(utt_id + " " + pjoin(speaker_dir, sub, wav) + "\n")

for speaker in ufa_train_spkrs:
    # This dir should be wherever you put your fixed wav files.
    speaker_dir = pjoin(UFA, "audio_fixed", speaker)
    wav_files = os.listdir(speaker_dir)
    for wav in wav_files:
        utt_id = wav[:-4]
        train_wavscp.write(utt_id + " " + pjoin(speaker_dir, wav) + "\n")

for speaker in ufa_test_spkrs:
    # This dir should be wherever you put your fixed wav files.
    speaker_dir = pjoin(UFA, "audio_fixed", speaker)
    wav_files = os.listdir(speaker_dir)
    for wav in wav_files:
        utt_id = wav[:-4]
        test_wavscp.write(utt_id + " " + pjoin(speaker_dir, wav) + "\n")
