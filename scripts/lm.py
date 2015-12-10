import re
import glob
import sys
import csv
from subprocess import call
from os.path import basename, join as pjoin

""" Script to generate LM from text files using SRILM. Assumes you have SRILM
installed and that it's on your path. All files are produced in current working
directory.

Usage:
    python lm.py <ufa_txt_dir> <atcosim_txt_dir> <n_order> <test_file>

ufa_txt_dir: where the txt files for UFA are located
atcosim_txt_dir: the TXTdata dir for atcosim
n_order: what order n-grams should be learned
test_file: txt file to calculate perplexity on

NOTE: on my machine, `compute_best_mix` wouldn't run using awk, so I had to
change 

#!/usr/bin/awk -f to #!/usr/bin/env gawk -f

(this also requires that you have gawk installed).

"""


def preproc_txt(text_dir):
    """Outputs combined train file as `train.txt`. Remove UFA tags and 
    lowercase.
    """
    txt_files = glob.glob(text_dir + '/*.txt')
    pattern1 = re.compile('\|[^\s]+') # Remove tags from text
    pattern2 = re.compile('_[^\s]+') # remove silence and phones
    combine_args = "cat {} > corpus.txt".format(' '.join(txt_files))
    call(combine_args, shell=True)
    with open('ufatrain.txt', 'w+') as train:
        with open('corpus.txt') as in_file:
            for line in in_file:
                outline = re.sub(pattern1, '', line)
                outline = re.sub(pattern2, '', outline)
                train.write(outline.lower())
    call("rm corpus.txt", shell=True)

def make_atcosim_train(dirname):
    # dirname is TXTdata directory
    with open('atctrain.txt', 'w+') as train:
        with open(pjoin(dirname,'fulldata.csv')) as csvfile:
            reader = csv.reader(csvfile)
            reader.next() # skip header
            for row in reader:
                train.write(row[6] + '\n')
    
def make_ufa_lm(n_order):
    """Outputs LM as `ufalm.gz`. Uses witten-bell discounting"""
    lm_args = ("ngram-count -text ufatrain.txt -lm ufalm.gz -order {} " +
               "-wbdiscount1 -wbdiscount2 -wbdiscount3 -wbdiscount4 " +
               "-wbdiscount5 -write-vocab vocab").format(n_order)
    call(lm_args, shell=True)
    call("rm ufatrain.txt", shell=True)
    
def make_atc_lm(n_order):
    """Outputs LM as `atclm.gz`. Uses witten-bell discounting"""
    lm_args = ("ngram-count -text atctrain.txt -lm atclm.gz -order {} " +
               "-wbdiscount1 -wbdiscount2 -wbdiscount3 -wbdiscount4 " +
               "-wbdiscount5 -vocab vocab").format(n_order)
    call(lm_args, shell=True)
    call("rm atctrain.txt", shell=True)

def make_test_corpus(text_file):
    # UFA_DE-test.trans
    with open('test.txt', 'w+') as test:
        with open(text_file) as in_file:
            for line in in_file:
                test.write(line.lower().split(' (')[0] + '\n')

def interpolate(n_order):
    """ Get the perplexity for each lm on the test set and then interpolate"""
    lm1_args = "ngram -debug 2 -order 5 -unk -lm ufalm.gz -ppl test.txt > ufalm.ppl"
    lm2_args = "ngram -debug 2 -order 5 -unk -lm atclm.gz -ppl test.txt > atclm.ppl"
    call(lm1_args, shell=True)
    call(lm2_args, shell=True)
    best_mix_args = "compute-best-mix ufalm.ppl atclm.ppl > best-mix.ppl"
    call(best_mix_args, shell=True)
    with open('best-mix.ppl') as f:
        line = f.readline()
    best_lambdas = [l.replace('(','').replace(')','') for l in line.split()[-2:]]
    mix_args = ("ngram -order {} -unk -lm ufalm.gz -lambda {} " +
                "-mix-lm atclm.gz -write-lm mixed_lm.gz").format(
                    n_order, best_lambdas[0])
    call(mix_args, shell=True)

def main(ufa_txt_dir, atcosim_txt_dir, n_order, test_file):
    # preprocess UFA data, produce ufatrain.txt
    preproc_txt(ufa_txt_dir) 
    # make LM for UFA, produce ufamodel.gz, vocab
    make_ufa_lm(n_order) 
    # preprocess atcosim data, produce atctrain.txt
    make_atcosim_train(atcosim_txt_dir)
    # make LM for atcosim, using vocab from ufa, so any word not occuring
    # in ufatrain is removed
    make_atc_lm(n_order)
    call("rm vocab", shell=True)
    # produce test.txt
    make_test_corpus(test_file)
    # get best interpolation weights and produce mixed_lm.gz
    interpolate(n_order)
    call("rm *.ppl", shell=True)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4])
    
