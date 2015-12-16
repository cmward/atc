import ebnf
import glob
import sys
import re
import operator
from collections import defaultdict
from itertools import izip
from os.path import basename
from subprocess import call, check_output
from pyparsing import *

""" Script to extract lattices/n-best lists from kaldi decoding
and rescore them based on (partial) parses of the hypothesis
using the UFA grammar.

Kaldi latbin needs to be on PATH.

Usage:
    python rescore.py def <ebnf_file> <lat_dir> <abs_pen>
"""
def flatten(lst):
    """Flatten a nested list"""
    # https://stackoverflow.com/questions/10823877/
    # what-is-the-fastest-way-to-flatten-arbitrarily-nested-lists-in-python
    for i in lst:
        if isinstance(i, list) or isinstance(i, tuple):
            for j in flatten(i):
                yield j
        else:
            yield i

def make_nbest(lat_dir):
    """ Get the n-best paths from the lattices produced by kaldi.
    Writes hypotheses to n.nb.txt for each lattice archive in lat_dir.
    """
    lats = glob.glob(lat_dir + "/lat.*.gz")
    for lat in lats:
        fn = basename(lat)
        n = ''.join(re.findall('\d+', fn))
        args = 'lattice-to-nbest --acoustic-scale=0.001 --n=5 "ark:gunzip -c {ld}/lat.{n}.gz|" ark,t:{ld}/{n}.nbest ; nbest-to-linear ark:{ld}/{n}.nbest ark,t:{ld}/{n}.ali ark,t:{ld}/{n}.words ark,t:{ld}/{n}.lmscore ark,t:{ld}/{n}.acscore ; utils/int2sym.pl -f 2- data/lang_final/words.txt {ld}/{n}.words > {n}.nb.txt'.format(n=n, ld=lat_dir)
        call(args, shell=True)

def write_scores(lat_dir):
    nbests = glob.glob('*.nb.txt')
    for nbest in nbests:
        fn = basename(nbest)
        n = ''.join(re.findall('\d+', fn))
        with open('{}.tmp'.format(n), 'w+') as tmp:
            lms = '{}/{}.lmscore'.format(lat_dir, n)
            acs = '{}/{}.acscore'.format(lat_dir, n)
            with open(lms) as f1, open(acs) as f2:
                for l, a in izip(f1, f2):
                    lscore = l.split()[1]
                    ascore = a.split()[1]
                    tmp.write("{} {}\n".format(lscore, ascore))
        with open(nbest) as nb, open('{}.tmp'.format(n)) as tmp:
            with open("{}.nb.scores.txt".format(n), 'w+') as s:
                for hyp, score in izip(nb, tmp):
                    s.write("{} {}\n".format(hyp.strip(), score.strip()))

def rescore(grammar, abs_pen=None):
    g = ebnf.parse(grammar)
    print "Loaded grammar from {}".format(grammar)
    nbests = glob.glob('*.nb.scores.txt')
    for nbest in nbests:
        fn = basename(nbest)
        n = ''.join(re.findall('\d+', fn))
        with open(nbest) as nb, open('{}.nb.rescored-abs.txt'.format(n), 'w+') as rescored:
            total = check_output("wc -l {}".format(nbest), shell=True).split()[0]
            for i,line in enumerate(nb):
                line = line.split()
                lsc, asc = line[-2:]
                line = line[:-2]
                score = float(lsc) + 0.001 * float(asc)
                hyp_id = line[0]
                hyp = ' '.join(line[1:])
                print "Parsing sentence {} of {}...".format(i+1, total)
                # find partial parses of hyp and rescore
                matches = []
                for subg in g:
                    match = g[subg].searchString(hyp)
                    matches.append(match.asList())
                matches = list(flatten(matches))
                not_matched = len([word for word in hyp.split() if word not in matches])
                if abs_pen:
                    if not_matched >= 1:
                        score -= 2.5
                else:
                    if not_matched >= 1:
                        score -= 0.5 * not_matched
                rescored.write("{} {}\n".format(hyp_id, score))

def write_new_best():
    #score_files = glob.glob('*.nb.rescored.txt')
    score_files = ['1.nb.rescored.txt', '10.nb.rescored.txt', '11.nb.rescored.txt']
    hyps = glob.glob('*.nb.txt')
    score_dict = defaultdict(list)
    for score_file in score_files:
        hyp_file = [hyp for hyp in hyps if hyp[:4] == score_file[:4]][0]
        hyp_lines = open(hyp_file).readlines()
        with open(score_file) as sf:
            for score_line in sf:
                hype_line = [h for h in hyp_lines if h.split()[0] == score_line.split()[0]][0]
                hyp = ' '.join(hype_line.split()[1:])
                score = score_line.split()[1]
                utt_id = '-'.join(score_line.split('-')[:2])
                score_dict[utt_id].append((score,hyp))
    with open('test.hyp', 'w+') as out:
        for utt in score_dict.iterkeys():
            best = ('', 0)
            for score_hyp_pair in score_dict[utt]:
                hyp = score_hyp_pair[1]
                score = score_hyp_pair[0] 
                if score > best[1]:
                    best = (hyp, score)
            out.write("{} {}\n".format(utt, best[0]))

def reformat_ref_hyp(ref, hyp):
    with open(ref) as r, open('new.ref', 'w+') as new:
        for line in r:
            line = line.split()
            new.write("{} ({})\n".format(' '.join(line[1:]), line[0]))
    with open(hyp) as h, open('new.hyp', 'w+') as new:
        for line in h:
            line = line.split()
            new.write("{} ({})\n".format(' '.join(line[1:]), line[0]))

        
def main(ebnf_file, lat_dir, abs_pen=None):
    make_nbest(lat_dir)
    write_scores(lat_dir)
    rescore(ebnf_file, abs_pen=abs_pen)
    #write_new_best()
        
if __name__ == "__main__":
    # main('grammar/full_grammar.ebnf','exp/atc_tri3/decode_test', 0)
    main(sys.argv[1], sys.argv[2], abs_pen=int(sys.argv[3]))
