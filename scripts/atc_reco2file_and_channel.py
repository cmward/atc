# Generates the reco2file_and_channel file for a given pizza data set.

import os, re, sys

# dataset should be 'train' or 'devtest'.
dataset = sys.argv[1]

# Set as the raw version of the transcripts.
transcript = open("".join([dataset, "/transcript/pizza_", dataset]))

# Makes the temp directories if they don't exist.
data_path = "".join(["data/", dataset, "/pizza_tmp"])
if not os.path.exists(data_path):
    os.mkdir(data_path)
    
# Creates the 'reco2file_and_channel' file
reco2file = open(data_path + "/reco2file_and_channel", "w")
lines = []

# Because the recording ID is the same as the wav file name, and
# since there is only a single channel, the file is written in the
# following format:
#       wav_name wav_name A
for line in transcript.readlines():
    match = re.match("(.*?) \((.*?)\)", line)
    rec_id = match.group(2)
    lines.append(" ".join([rec_id, rec_id, "A\n"]))

reco2file.writelines(lines)
