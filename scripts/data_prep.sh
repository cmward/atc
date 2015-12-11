#!/bin/bash

## To be run from the project directory.

# Usage:
#	sh data_prep <ufa-dir> <ufa-audio-dir> <atcosim-dir> /
#			<broadcast-dir> <broadcast-transcript-dir> <partition-path> <data-path>
# For example:
#	sh data_prep.sh corpora/UFA_DE corpora/UFA_DE/audio_fixed corpora/ATCOSIM /
#		corpora/broadcast corpora/broadcast/hub4_eng_train_trans data_partitioning data
#

### Set up sorting.
export LANG=C; export LC_ALL=C

ufa=$1
ufa_audio=$2
atcosim=$3
broadcast=$4
broadcast_trans=$5
partitions=$6
data_path=$7

python scripts/atc_text.py $ufa $atcosim $data_path
python scripts/atc_wavscp.py $ufa_audio $atcosim $partitions $data_path
python scripts/atc_segments_and_reco.py $data_path
python scripts/atc_utt2spk.py $ufa $atcosim $data_path
python scripts/broadcast_kaldi_files.py $broadcast $broadcast_trans $data_path

# Combine the 'atc' and 'broadcast' directories into a 'train' directory.
atc_path=$data_path/atc
broadcast_path=$data_path/broadcast
train_path=$data_path/train
mkdir -p $train_path

cat $atc_path/text $broadcast_path/text | sort -u > $train_path/text
cat $atc_path/segments $broadcast_path/segments | sort -u > $train_path/segments
cat $atc_path/wav.scp $broadcast_path/wav.scp | sort -u > $train_path/wav.scp
cat $atc_path/reco2file_and_channel $broadcast_path/reco2file_and_channel | sort -u > $train_path/reco2file_and_channel
cat $atc_path/utt2spk $broadcast_path/utt2spk | sort -u > $train_path/utt2spk

# Sort the files of the 'test' directory.
test_path=$data_path/test

for f in text segments wav.scp reco2file_and_channel utt2spk; do
  sort $test_path/$f -o $test_path/$f
done

# Generate the spk2utt files.
utils/utt2spk_to_spk2utt.pl $train_path/utt2spk > $train_path/spk2utt
utils/utt2spk_to_spk2utt.pl $test_path/utt2spk > $test_path/spk2utt

# Ensures segments are present in all files.
bash utils/fix_data_dir.sh $train_path
bash utils/fix_data_dir.sh $test_path

echo ATC data preparation succeeded.