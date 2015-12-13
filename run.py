# Pipeline script for ATC data

import os, shutil
from os.path import join as pjoin
from path import *
from subprocess import call

### Requires these defined in path.py or elsewhere:
#
# PROJECT_ROOT = os.curdir
# SCRIPTS = pjoin(PROJECT_ROOT, 'scripts')
# UFA = pjoin(PROJECT_ROOT, 'corpora/UFA_DE')
# UFA_TXT = pjoin(UFA, 'trans')
# UFA_AUDIO = pjoin(UFA, 'audio_fixed')
# ATCOSIM = pjoin(PROJECT_ROOT, 'corpora/ATCOSIM')
# ATCOSIM_AUDIO = pjoin(ATCOSIM, 'WAVdata_fixed')
# ATCOSIM_TXT = pjoin(ATCOSIM, 'TXTdata')
# BROADCAST = pjoin(PROJECT_ROOT, 'corpora/broadcast')
# BROADCAST_TRANSCRIPTS = pjoin(BROADCAST, 'hub4_eng_train_trans')
# GENERATED = 'corpora/generated'


# Aligns the model and aves the alignment data.
def align_cmd(src_dir, align_dir):
    command = " ".join(["sh steps/align_si.sh --nj 4 data/train data/lang_final",
                        src_dir, align_dir])
    return command

# Utilizes the given alignment data to generate a new model.
def train_deltas_cmd(align_dir, exp_dir):
    command = " ".join(["sh steps/train_deltas.sh 3200 30000 data/train data/lang_final",
                        align_dir, exp_dir])
    return command


## Data Preparation
data_args = " ".join(["sh scripts/data_prep.sh", UFA, UFA_AUDIO, ATCOSIM, ATCOSIM_AUDIO,
                      BROADCAST, BROADCAST_TRANSCRIPTS, "data_partitioning", "data"])
call(data_args, shell=True)

## Dictionary preparation.
# No scripts right now.

## Language Preparation
call('bash utils/prepare_lang.sh data/local/dict "<unk>" data/local/lang data/lang', shell=True)

## Create language model.
cat_args = " ".join(['cat', pjoin(UFA_TXT, 'UFA_DE-deFemale.trans'),
                     pjoin(UFA_TXT, 'UFA_DE-deMale.trans'),
                     '>', pjoin(UFA_TXT, 'UFA_DE-train.trans')])
call(cat_args, shell=True)
lm_args = " ".join(['python', 'scripts/lm.py', GENERATED, ATCOSIM_TXT, pjoin(UFA_TXT, 'UFA_DE-train.trans')])
call(lm_args, shell=True)

# Format language model.
call("sh utils/format_lm_sri.sh data/lang mixed_lm.gz data/local/dict/lexicon.txt data/lang_final",
     shell=True)

# os.system("bash utils/fix_data_dir.sh data/devtest")

# Compute MFCC features for training and devtest data.
for dataset in ["train", "test"]:
    args = ("sh steps/make_mfcc.sh --nj 4 data/" + dataset + " exp/make_mfcc/"
            + dataset + " mfcc")
    call(args, shell=True)
    args = "".join(["sh steps/compute_cmvn_stats.sh data/", dataset, " exp/make_mfcc/", dataset, " mfcc"])
    call(args, shell=True)
    # os.system("".join(["bash utils/fix_data_dir.sh data/", dataset]))

## Train monophone model.
call("sh steps/train_mono.sh --nj 4 data/train data/lang_final exp/mono")

## Train triphone model, round 1.
##os.system(align_cmd("exp/mono", "exp/mono_ali"))
##os.system(train_deltas_cmd("exp/mono_ali", "exp/tri1"))
##
#### Decoding, round 1.
##os.system("sh utils/mkgraph.sh data/lang_final exp/tri1 exp/tri1/graph_tgpr")
##os.system('sh steps/decode.sh --nj 30 --cmd "utils/run.pl" exp/tri1/graph_tgpr data/devtest exp/tri1/decode_devtest')
##
#### Train triphone model, round 2.
##os.system(align_cmd("exp/tri1", "exp/tri1_ali"))
##os.system(train_deltas_cmd("exp/tri1_ali", "exp/tri2"))
##
#### Decoding, round 2.
##os.system("sh utils/mkgraph.sh data/lang_final exp/tri2 exp/tri2/graph_tgpr")
##os.system('sh steps/decode.sh --nj 30 --cmd "utils/run.pl" exp/tri2/graph_tgpr data/devtest exp/tri2/decode_devtest')
##
#### Get WER 
### Score the decoding results.
##os.system("sh score.sh data/devtest  exp/tri1/graph_tgpr exp/tri1/decode_devtest")
##os.system("sh score.sh data/devtest  exp/tri2/graph_tgpr exp/tri2/decode_devtest")
##
### Print word error rate for scored lattices.
##exp_path = "exp/tri2/decode_devtest/"
##filenames = os.listdir(exp_path)
##for filename in filenames:
##    if filename.startswith("wer"):
##	wer_file = open(exp_path + filename)
##	print(wer_file.readlines()[1])
##	wer_file.close()
