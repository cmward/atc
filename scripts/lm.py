import re
import glob
import sys
from subprocess import call

""" Script to generate LM from text files using SRILM. Assumes you have SRILM
installed and that it's on your path.

Usage:
    python lm.py <text_dir> <output_dir> <n_order>

text_dir: where the txt files to learn the LM are located
output_dir: where the LM should be written
n_order: what order n-grams should be learned

TODO: Interpolate ufa and atcosim models
"""


def preproc_txt(txt_files):
    """Outputs combined train file as `train.txt`. Remove UFA tags and 
    lowercases.
    """
    pattern1 = re.compile('\|[^\s]+') # Remove tags from text
    pattern2 = re.compile('_[^\s]+') # remove silence and phones
    combine_args = "cat {} > corpus.txt".format(' '.join(txt_files))
    call(combine_args, shell=True)
    with open('train.txt', 'w+') as train:
        with open('corpus.txt') as in_file:
            for line in in_file:
                outline = re.sub(pattern1, '', line)
                outline = re.sub(pattern2, '', outline)
                train.write(outline.lower())
    call("rm corpus.txt", shell=True)

def make_lm(text_dir, output_model, n_order):
    """Outputs LM as `{output_model}`. Uses witten-bell discounting"""
    txt_files = glob.glob(text_dir + '/*.txt')
    preproc_txt(txt_files)
    lm_args = ("ngram-count -text train.txt -lm {} -order {} " +
               "-wbdiscount1 -wbdiscount2 -wbdiscount3 -wbdiscount4 " +
               "-wbdiscount5").format(output_model, n_order)
    call(lm_args, shell=True)
    call("rm train.txt", shell=True)
    
def main(text_dir, output_dir, n_order):
    make_lm(text_dir, output_dir, n_order)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]))
    
