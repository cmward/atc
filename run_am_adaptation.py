import os, shutil
from os.path import join as pjoin
from path import *
from subprocess import call

train_subset_dir = '' #INSERT NAME

#fmllr
fmllr_command = ' '.join(['sh steps/align_fmllr.sh --nj 4', train_subset_dir, 'data/lang', 'exp/tri3', 'exp/tri3_ali'])
call(fmllr_command, shell=True)

#ubm
#600 is number of Gaussian used in rm recipe, not sure what is best
ubm_command = ' '.join(['sh steps/train_ubm.sh 600', train_subset_dir, 'data/lang', 'exp/tri3_ali', 'exp/ubm'])
call(ubm_command, shell=True)

#train sgmm
#again just guessing on the numbers, taken from usage example
train_sgmm_command = ' '.join(['sh steps/train_sgmm2.sh --nj 4 5000 8000', train_subset_dir, 'data/lang', 'exp/tri3_ali', 'exp/ubm/final.ubm', 'exp/sgmm'])
call(train_sgmm_command, shell=True)

#mkgraph
#check which lang dir
graph_command = 'sh steps/mkgraph.sh data/lang_final exp/sgmm exp/sgmm/graph_tgpr'
call(graph_command, shell=True)

#decode
decode_command = ' '.join(['sh steps/decode_sgmm2.sh', 'exp/sgmm/graph_tgpr', datadir, 'exp/sgmm/decode_tgpr'])
call(decode_command, shell=True)

#align sgmm--if we want to do further training
# align_sgmm_command = ' '.join(['sh steps/align_sgmm2.sh --nj 4 --transform-dir exp/tri3_ali', train_subset_dir, 'data/lang', 'exp/sgmm', 'exp/sgmm_ali'])
# call(align_sgmm_command, shell=True)

## they also have mmi_sgmm training and rescoring
## again not sure if we need that

#WER stuff





