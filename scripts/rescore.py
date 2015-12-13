import ebnf
import sys
from subprocess import call
from pyparsing import *

""" Script to extract lattices/n-best lists from kaldi decoding
and rescore them based on (partial) parses of the hypothesis
using the UFA grammar.

"""

class Grammar(object):
    def __init__(self, ebnf_file):
        self.parser = ebnf.parse(ebnf_file)

    def scan(self, string):
        output = parser['atc'].searchString(string)
        return output

def nbest(n, lat_dir):
    """ Get the n-best list from the lattices produced by kaldi.
    Returns the top n hypotheses and their scores. 
    """
    pass

def rescore(nbest, grammar, penalty=0.01):
    """nbest is a list of (hypothesis, score) pairs."""
    for hyp, score in nbest:
        parse = grammar.scan(hyp)
        
