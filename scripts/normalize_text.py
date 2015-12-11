import re

word_map = { '[EMPTY]' : '<sil>',
             '[FRAGMENT]' : '<unk>',
             '[HNOISE]' : '<unk>',
             '[NONSENSE]' : '<unk>',
             '[UNKNOWN]' : '<unk>',
             '<FL>' : '<unk>',
             '</FL>' : '',
             '<OT>' : '',
             '</OT>' : '',
             'alfa': 'alpha'}

def normalize_atcosim(line, word_map):
    words = line.split()
    for i in range(len(words)):
        if words[i].startswith("@"):
            words[i] = "<unk>"
        elif words[i].startswith("=") or words[i].endswith("="):
            words[i] = "<unk>"
        words[i] = word_map.get(words[i], words[i])
    norm_line = " ".join(words)
    match = re.search("~[a-z]( ~[a-z])*", norm_line)
    if match:
        acro = re.sub('~([a-z]) ?', '\\1.', match.group())
        norm_line = re.sub(match.group(), acro, norm_line)
    return norm_line

# Does little at the moment.
def normalize_ufa(line):
    return line.lower()

# Removes markup, making the following transformations:
#   ((word)) >> <unk>
#   #word# >> word
#   [environment noise] >> <unk>
#   {human noise} >> <unk>
#   @proper_noun >> proper_noun
#   +word+ >> word 
#   *made-up word* >> made-up word
#   wo- >> <unk>
def normalize_broadcast(line):
    norm_line = re.sub('@|#|\*|\.', '', line)
    norm_line = re.sub('( -\w*)|(\w*- )|(\+.*?\+)|(\{.*?\})|(\[.*?\])|(\(\(.*?\)\))', ' <unk> ', norm_line)
    return " ".join(norm_line.split())
