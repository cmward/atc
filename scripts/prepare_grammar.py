import re
import glob
import sys
from subprocess import call

""" Script to preprare convert .hg grammars into one EBNF grammar to be used
with pyparsing.

Usage:
    python <hg_dir>

<hg_dir> : directory where .hg files are located

Produces `full_grammar.ebnf`
"""

def make_big_hg(hg_dir):
    """Combine all of the .hg files in hg_dir into a big .hg file."""
    hgs = glob.glob(hg_dir + '/*.hg')
    args = "cat {} > full_grammar.hg".format(' '.join(hgs))
    call(args, shell=True)

def preproc_hg(hg_file):
    """ Remove UFA tags from grammar."""
    tag_pattern = re.compile('\.*\/[^\s\)\];]+') # Remove tags from text
    label_pattern = re.compile('{.+}') # Remove labels
    with open(hg_file) as hg, open('tmp.hg', 'w+') as tmp:
        for line in hg:
           outline = re.sub(tag_pattern, '', line)
           outline = re.sub(label_pattern, '', outline)
           tmp.write(outline.lower().replace('-', '_'))
    with open('tmp.hg') as infile, open(hg_file, 'w+') as outfile:
        for line in infile:
            outfile.write(line)
    call("rm tmp.hg", shell=True)

def convert_hg(hg_file, ebnf_file):
    """ Convert .hg grammar to EBNF grammar.
    """
    with open(hg_file) as hg, open(ebnf_file, 'w+') as ebnf:
        for line in hg:
            if line.startswith('#'): # comment
                continue
            elif line.startswith('<'): #grammar reference
                continue
            else:
                line = [t for t in re.split('([\(\[\]\)\s])', line.strip())
                        if t not in ['', ' ']]
                ebnf.write(convert(line) + '\n')

def convert(line):
    out = []
    for i, token in enumerate(line):
        no_comma = [']', ')', '|', ':', ';']
        if token == ':':
            out.append('=')
        elif token == '[':
            out.append(token)
        elif token == ']':
            out.append(token)
            try:
                if line[i+1] not in no_comma:
                    out.append(',')
            except IndexError:
                continue
        elif token == '(':
            out.append(token)
        elif token == ')':
            out.append(token)
            try:
                if line[i+1] not in no_comma:
                    out.append(',')
            except IndexError:
                continue
        elif token == '|':
            out.append(token)
        elif token == ';':
            out.append(token)
        elif token.startswith('$'):
            # non-terminal definition
            if token.endswith(':'):
                out.append(token[1:-1])
                out.append('=')
            # nonterminal
            else:
                out.append(token[1:])
                try:
                    if line[i+1] not in no_comma:
                        out.append(',')
                except IndexError:
                    continue
        else:
            # terminal
            out.append('"{}"'.format(token))
            try:
                if line[i+1] not in no_comma:
                    out.append(',')
            except IndexError:
                continue
    return ' '.join(out)

def convert_pass_two(ebnf_file):
    """Make a second pass over the converted file to insert end of line commas."""
    no_comma_prev = ['|', '=', ';']
    no_comma_line = ['|']
    with open(ebnf_file) as ebnf, open('tmp.ebnf') as tmp:
        prev = src.next()
        for line in ebnf:
            # do some stuff
            line = line.split()
            prev = prev.split()
            if (prev[-1] not in no_comma_prev and line[-1] not in no_comma_line
                    and not '=' in line):
                prev.append(',')
            tmp.write(prev)
            prev = line

def main(hg_dir):
    make_big_hg(hg_dir)
    preproc_hg('full_grammar.hg')
    convert_hg('full_grammar.hg', 'full_grammar.ebnf')

if __name__ == "__main__":
    main(sys.argv[1])
