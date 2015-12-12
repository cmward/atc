import ebnf
import sys
from subprocess import call
from pyparsing import *

""" Script to extract lattices/n-best lists from kaldi decoding
and rescore them based on (partial) parses of the hypothesis
using the UFA grammar.

"""

def read_ebnf(ebnf_file):
    """ Read in ebnf grammar and create pyparsing grammar.
    """
    p = ebnf.parse(ebnf_file)
    return p

class Grammar(object):
    def __init__(self, ebnf_file):
        self.parser = ebnf.parse(ebnf_file)

    def scan(self, string):
        output = parser['atc'].searchString(string)
        return output

def nbest(lat_dir):
    """ Get the n-best list from the lattices produced by kaldi
    """
    pass

