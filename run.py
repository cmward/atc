# Pipeline script for various models trained on German-accented ATC data and American-accented
# Broadcast News data. All models are tested on German-accented ATC data.
# Authors: Matthew Garber, Meital Singer, and Chris Ward

import os
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
def align_cmd(train_dir, src_dir, align_dir):
    command = ' '.join(['sh steps/align_si.sh --nj 4', train_dir, 'data/lang_final',
                        src_dir, align_dir])
    return command

# Utilizes the given alignment data to generate a new model.
def train_deltas_cmd(train_dir, align_dir, exp_dir):
    command = ' '.join(['sh steps/train_deltas.sh 2500 20000', train_dir, 'data/lang_final',
                        align_dir, exp_dir])
    return command


## Data Preparation
data_args = ' '.join(['sh scripts/data_prep.sh', UFA, UFA_AUDIO, ATCOSIM, ATCOSIM_AUDIO,
                      BROADCAST, BROADCAST_TRANSCRIPTS, 'data_partitioning', 'data'])
call(data_args, shell=True)

## Dictionary preparation.
# No scripts right now.

## Language Preparation
call('bash utils/prepare_lang.sh data/local/dict "<unk>" data/local/lang data/lang', shell=True)

## Create language model.
cat_args = ' '.join(['cat', pjoin(UFA_TXT, 'UFA_DE-deFemale.trans'),
                     pjoin(UFA_TXT, 'UFA_DE-deMale.trans'),
                     '>', pjoin(UFA_TXT, 'UFA_DE-train.trans')])
call(cat_args, shell=True)
lm_args = ' '.join(['python', 'scripts/lm.py', GENERATED, ATCOSIM_TXT, pjoin(UFA_TXT, 'UFA_DE-train.trans')])
call(lm_args, shell=True)

# Format language model.
call('sh utils/format_lm_sri.sh data/lang mixed_lm.gz data/local/dict/lexicon.txt data/lang_final',
     shell=True)


## os.system('bash utils/fix_data_dir.sh data/test')

# Compute MFCC features for all data.
for dataset in ['atc', 'broadcast', 'train', 'test']:
    args = ('sh steps/make_mfcc.sh --nj 12 data/' + dataset + ' exp/make_mfcc/'
            + dataset + ' mfcc')
    call(args, shell=True)
    args = ''.join(['sh steps/compute_cmvn_stats.sh data/', dataset, ' exp/make_mfcc/', dataset, ' mfcc'])
    call(args, shell=True)
    # Ensure segments are present in all relevant files.
    call(''.join(['bash utils/fix_data_dir.sh data/', dataset]))

#################################
#       BASELINE TRAINING       #
#################################

# The baseline model is an HMM/GMM triphone model.

# Train monophone model.
call('sh steps/train_mono.sh --nj 4 data/train data/lang_final exp/mono', shell=True)

# Train triphone model, round 1.
call(align_cmd('data/train', 'exp/mono', 'exp/mono_ali'), shell=True)
call(train_deltas_cmd('data/train', 'exp/mono_ali', 'exp/tri1'), shell=True)

# Train triphone model, round 2.
call(align_cmd('data/train', 'exp/tri1', 'exp/tri1_ali'), shell=True)
call(train_deltas_cmd('data/train', 'exp/tri1_ali', 'exp/tri2'), shell=True)

# Train triphone model, round 3.
call(align_cmd('data/train', 'exp/tri2', 'exp/tri2_ali'), shell=True)
call(train_deltas_cmd('data/train', 'exp/tri2_ali', 'exp/tri3'), shell=True)

# Make the graph and decode.
call('sh utils/mkgraph.sh data/lang_final exp/tri3 exp/atc_tri3/graph_tgpr', shell=True)
call('sh steps/decode.sh --nj 12 exp/tri3/graph_tgpr data/test exp/tri3/decode_test', shell=True)

######### WER?

#################################
#    ATC-ONLY MODEL TRAINING    #
#################################

# The ATC-Only model is an HMM/GMM triphone model trained only on ATC data.

# Train monophone model.
call('sh steps/train_mono.sh --nj 4 data/atc data/lang_final exp/atc_mono', shell=True)

# Train triphone model, round 1.
call(align_cmd('data/atc', 'exp/atc_mono', 'exp/atc_mono_ali'), shell=True)
call(train_deltas_cmd('data/atc', 'exp/atc_mono_ali', 'exp/atc_tri1'), shell=True)

# Train triphone model, round 2.
call(align_cmd('data/atc', 'exp/atc_tri1', 'exp/atc_tri1_ali'), shell=True)
call(train_deltas_cmd('data/atc', 'exp/atc_tri1_ali', 'exp/atc_tri2'), shell=True)

# Train triphone model, round 3.
call(align_cmd('data/atc', 'exp/atc_tri2', 'exp/atc_tri2_ali'), shell=True)
call(train_deltas_cmd('data/atc', 'exp/atc_tri2_ali', 'exp/atc_tri3'), shell=True)

# Make the graph and decode.
call('sh utils/mkgraph.sh data/lang_final exp/atc_tri3 exp/atc_tri3/graph_tgpr', shell=True)
call('sh steps/decode.sh --nj 4 exp/atc_tri3/graph_tgpr data/test exp/atc_tri3/decode_test', shell=True)

########################################
#    BROADCAST MAP-ADAPTED TRAINING    #
########################################

# This model is trained only on the Broadcast News data and than adapted to the
# ATC data with Maximum A Posteriori training.

# Train monophone model.
call('sh steps/train_mono.sh --nj 4 data/broadcast data/lang_final exp/broadcast_mono', shell=True)

# Train triphone model, round 1.
call(align_cmd('data/broadcast', 'exp/broadcast_mono', 'exp/broadcast_mono_ali'), shell=True)
call(train_deltas_cmd('data/broadcast', 'exp/broadcast_mono_ali', 'exp/broadcast_tri1'), shell=True)

# Train triphone model, round 2.
call(align_cmd('data/broadcast', 'exp/broadcast_tri1', 'exp/broadcast_tri1_ali'), shell=True)
call(train_deltas_cmd('data/broadcast', 'exp/broadcast_tri1_ali', 'exp/broadcast_tri2'), shell=True)

# Train triphone model, round 3.
call(align_cmd('data/broadcast', 'exp/broadcast_tri2', 'exp/broadcast_tri2_ali'), shell=True)
call(train_deltas_cmd('data/broadcast', 'exp/broadcast_tri2_ali', 'exp/broadcast_tri3'), shell=True)

# Use MAP adaptation.
call('sh steps/train_map.sh data/atc data/lang_final exp/tri3_ali_adapt exp/tri4_adapt', shell=True)

# Make the graph and decode.
call('sh utils/mkgraph.sh data/lang_final exp/tri4_adapt exp/tri4_adapt/graph_tgpr', shell=True)
call('sh steps/decode.sh --nj 4 exp/tri4_adapt/graph_tgpr data/test exp/tri4_adapt/decode_test', shell=True)

#########################################
#              SGMM MODELS              #
#########################################

#----------SGMM+fMLLR Training----------#
# This model starts with alignments from
# the second round of the baseline model.
#---------------------------------------#

# Generate fMLLR transforms for the test data. This decoding can also be scored later.
call('sh utils/mkgraph.sh data/lang_final exp/tri2 exp/tri2/graph_tgpr', shell=True)
decode_fmllr_cmd = ' '.join(['sh', 'steps/decode_fmllr.sh', '--nj', '4', 'exp/tri2/graph_tgpr',
                             'data/test', 'exp/tri2/decode_fmllr'])
call(decode_fmllr_cmd, shell=True)

# The last script has a tendency to fail partway through, so we run part of it again.
decode_fmllr_cmd = ' '.join(['sh', '--si-dir', 'exp/tri2/decode_fmllr.si', 'steps/decode_fmllr.sh',
                             '--nj', '4', 'exp/tri2/graph_tgpr', 'data/test', 'exp/tri2/decode_fmllr2'])
call(decode_fmllr_cmd, shell=True)

# Create fMLLR alignments.
fmllr_command = ' '.join(['sh steps/align_fmllr.sh', '--nj 4', 'data/train', 'data/lang_final',
                          'exp/tri2', 'exp/tri2_ali_fmllr'])
call(fmllr_command, shell=True)

# Train UBM on fMLLR alignments.
ubm_command = ' '.join(['sh steps/train_ubm.sh 400', 'data/train', 'data/lang_final',
                        'exp/tri2_ali_fmllr', 'exp/ubm3a'])
call(ubm_command, shell=True)

# Train the SGMM with the UBM and fMLLR alignments on just ATC data.
sgmm_command = ' '.join(['sh', 'steps/train_sgmm2.sh', '--nj 4', '5000 8000', 'data/atc', 'data/lang_final',
                         'exp/tri2_ali_fmllr', 'exp/ubm3a/final.ubm', 'exp/sgmm3a'])
call(sgmm_command, shell=True)

# Make the graph and decode using the fMLLR transforms.
call('sh utils/mkgraph.sh data/lang_final exp/sgmm3a exp/sgmm3a/graph_tgpr', shell=True)
decode_sgmm_cmd = ' '.join(['sh steps/decode_sgmm2.sh', '--nj 4', '--transform-dir',
                            'exp/tri2/decode_fmllr2', 'exp/sgmm3a/graph_tgpr', 'data/atc',
                            'exp/sgmm3a/decode_test'])
call(decode_sgmm_cmd, shell=True)

#--------SGMM+SAT+fMLLR Training--------#
# This model starts with alignments from
# the first round of the baseline model.
#---------------------------------------#

# Train with SAT (Speaker Adaptive Training).
sat_command = ' '.join(['sh', 'steps/train_sat.sh', '1800', '9000', 'data/train', 'data/lang_final',
                        'exp/tri1_ali', 'exp/tri2_sat'])
call(sat_command, shell=True)

# Generate fMLLR transforms for the test data. This decoding can also be scored later.
call('sh utils/mkgraph.sh data/lang_final exp/tri2_sat exp/tri2_sat/graph_tgpr', shell=True)
decode_fmllr_cmd = ' '.join(['sh', 'steps/decode_fmllr.sh', '--nj', '4', 'exp/tri2_sat/graph_tgpr',
                             'data/test', 'exp/tri2_sat/decode_fmllr'])
call(decode_fmllr_cmd, shell=True)

# The last script has a tendency to fail partway through, so we run part of it again.
decode_fmllr_cmd = ' '.join(['sh', '--si-dir', 'exp/tri2_sat/decode_fmllr.si', 'steps/decode_fmllr.sh',
                             '--nj', '4', 'exp/tri2_sat/graph_tgpr', 'data/test', 'exp/tri2_sat/decode_fmllr2'])
call(decode_fmllr_cmd, shell=True)

# Create fMLLR alignments on just ATC data.
fmllr_command = ' '.join(['sh steps/align_fmllr.sh', '--nj 4', 'data/atc', 'data/lang_final',
                          'exp/tri2_sat', 'exp/tri2_sat_ali'])
call(fmllr_command, shell=True)

# Train UBM on ATC data and fMLLR alignments.
ubm_command = ' '.join(['sh steps/train_ubm.sh 600', 'data/atc', 'data/lang_final',
                        'exp/tri2_sat_ali', 'exp/ubm3b'])
call(ubm_command, shell=True)

# Train the SGMM with the UBM and fMLLR alignments
sgmm_command = ' '.join(['sh', 'steps/train_sgmm2.sh', '--nj 4', '5000 8000', 'data/atc', 'data/lang_final',
                         'exp/tri2_sat_ali', 'exp/ubm3b/final.ubm', 'exp/sgmm3b'])
call(sgmm_command, shell=True)

# Make the graph and decode using the fMLLR transforms.
call('sh utils/mkgraph.sh data/lang_final exp/sgmm3b exp/sgmm3b/graph_tgpr', shell=True)
decode_sgmm_cmd = ' '.join(['sh steps/decode_sgmm2.sh', '--nj 4', '--transform-dir',
                            'exp/tri2_sat/decode_fmllr2', 'exp/sgmm3b/graph_tgpr', 'data/atc',
                            'exp/sgmm3b/decode_test'])
call(decode_sgmm_cmd, shell=True)

#--------SGMM+SAT+fMLLR Training--------#
# This model starts with alignments from
# the second round of the baseline model.
#---------------------------------------#

# Train with SAT (Speaker Adaptive Training).
sat_command = ' '.join(['sh', 'steps/train_sat.sh', '1800', '9000', 'data/train', 'data/lang_final',
                        'exp/tri2_ali', 'exp/tri3_sat'])
call(sat_command, shell=True)

# Generate fMLLR transforms for the test data. This decoding can also be scored later.
call('sh utils/mkgraph.sh data/lang_final exp/tri3_sat exp/tri3_sat/graph_tgpr', shell=True)
decode_fmllr_cmd = ' '.join(['sh', 'steps/decode_fmllr.sh', '--nj', '4', 'exp/tri3_sat/graph_tgpr',
                             'data/test', 'exp/tri3_sat/decode_fmllr'])
call(decode_fmllr_cmd, shell=True)

# The last script has a tendency to fail partway through, so we run part of it again.
decode_fmllr_cmd = ' '.join(['sh', '--si-dir', 'exp/tri3_sat/decode_fmllr.si', 'steps/decode_fmllr.sh',
                             '--nj', '4', 'exp/tri3_sat/graph_tgpr', 'data/test', 'exp/tri3_sat/decode_fmllr2'])
call(decode_fmllr_cmd, shell=True)

# Create fMLLR alignments on just ATC data.
fmllr_command = ' '.join(['sh steps/align_fmllr.sh', '--nj 4', 'data/atc', 'data/lang_final',
                          'exp/tri3_sat', 'exp/tri3_sat_ali'])
call(fmllr_command, shell=True)

# Train UBM on ATC data and fMLLR alignments.
ubm_command = ' '.join(['sh steps/train_ubm.sh 600', 'data/atc', 'data/lang_final',
                        'exp/tri3_sat_ali', 'exp/ubm4a'])
call(ubm_command, shell=True)

# Train the SGMM with the UBM and fMLLR alignments
sgmm_command = ' '.join(['sh', 'steps/train_sgmm2.sh', '--nj 4', '5000 8000', 'data/atc', 'data/lang_final',
                         'exp/tri3_sat_ali', 'exp/ubm4a/final.ubm', 'exp/sgmm4a'])
call(sgmm_command, shell=True)

# Make the graph and decode using the fMLLR transforms.
call('sh utils/mkgraph.sh data/lang_final exp/sgmm4a exp/sgmm4a/graph_tgpr', shell=True)
decode_sgmm_cmd = ' '.join(['sh steps/decode_sgmm2.sh', '--nj 4', '--transform-dir',
                            'exp/tri3_sat/decode_fmllr2', 'exp/sgmm4a/graph_tgpr', 'data/atc',
                            'exp/sgmm4a/decode_test'])
call(decode_sgmm_cmd, shell=True)
