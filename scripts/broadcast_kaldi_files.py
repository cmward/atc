import os, re, sys
from os.path import join as pjoin
from normalize_text import *

"""

Generates the relevant training files for Kaldi.

Usage:
    python broadcast_kaldi_files <overall-broadcast-dir> <broadcast-transcripts-dir> <data_path>    

"""

def make_text_line(utt_id, utt):
    return " ".join([utt_id, utt + "\n"])

def make_utt2spk_line(utt_id, speaker):
    return " ".join([utt_id, speaker + "\n"])

def make_segments_line(utt_id, filename, start, end):
    return " ".join([utt_id, filename, start, end + "\n"])

def make_reco_line(filename):
    return " ".join([filename, filename, "A\n"])

def make_wavscp_line(filename, audio_dir):
    sph_pipe = "sph2pipe_v2.5/sph2pipe -f wav -p -c 1"
    return " ".join([filename, sph_pipe, audio_dir + "/" + filename + ".sph", "|\n"])

def main(broadcast_dir, broadcast_transcripts, data_path):
    train_path = pjoin(data_path, "broadcast")
    if not os.path.exists(train_path):
        os.makedirs(train_path)
    text = open(pjoin(train_path, "text"), "w")
    wavscp = open(pjoin(train_path, "wav.scp"), "w")
    segments = open(pjoin(train_path, "segments"), "w")
    utt2spk = open(pjoin(train_path, "utt2spk"), "w")
    reco = open(pjoin(train_path, "reco2file_and_channel"), "w")
    sph_dir1 = pjoin(broadcast_dir, "h4eng_sp_d1", "data")
    sph_dir2 = pjoin(broadcast_dir, "h4eng_sp_d2", "data")
    sph_dir3 = pjoin(broadcast_dir, "h4eng_sp_d3", "data")
    info = ()   # Stores info from the annotation
    utt = ""    # Stores the utterance

    trans_dirs = [subdir for subdir in os.listdir(broadcast_transcripts) if not "." in subdir]

    for trans_dir in trans_dirs:
        transcripts = os.listdir(pjoin(broadcast_transcripts, trans_dir))
        for transcript in transcripts:
            trans_file = open(pjoin(broadcast_transcripts, trans_dir, transcript))
            filename = transcript[:-4]
            utt_counter = 1
            for line in trans_file:
                low_line = line.lower()
                if low_line.startswith("<segment"):
                    info = re.search('segment s_time=([\d.]*) e_time=([\d.]*) speaker="([\.\'\-\w]*)"', low_line).groups()
                elif low_line.startswith("</segment"):
                    start, end, speaker = info[0], info[1], info[2]
                    utt_id = "-".join([speaker, filename, str(utt_counter)])
                    text.write(make_text_line(utt_id, normalize_broadcast(utt)))
                    utt2spk.write(make_utt2spk_line(utt_id, speaker))
                    segments.write(make_segments_line(utt_id, filename, start, end))
                    reco.write(make_reco_line(filename))
                    sph_pipe = "sph2pipe_v2.5/sph2pipe -f wav -p -c 1"
                    if (filename + ".sph") in sph_dir1:
                        wavscp.write(make_wavscp_line(filename, sph_dir1))
                    elif (filename + ".sph") in sph_dir2:
                        wavscp.write(make_wavscp_line(filename, sph_dir1))
                    else:
                        wavscp.write(make_wavscp_line(filename, sph_dir1))
                    utt = ""
                    utt_counter += 1
                elif not low_line.startswith("<"):
                    utt = utt + low_line.strip() + " "

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
