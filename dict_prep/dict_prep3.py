import os, nltk, sys
from nltk.corpus import cmudict
cmuprondict = cmudict.dict()

small_lexfile = open('lexicon_revised.txt', 'r')
oovfile = open('oov_revised.txt', 'r')
big_lexfile = open('full_lexicon.txt', 'w')
words = set()
entries = []

for line in small_lexfile.readlines():
	if 'OOV_WORD' in line:
		continue
	else:
		if 'ei r' in line:
			line = line.replace('ei r', 'ey r')
		entries.append(line.strip())
		words.add(line.split()[0])
small_lexfile.close()

for line in oovfile.readlines():
	entries.append(line.strip())
	words.add(line.split()[0])
oovfile.close()

for word in cmuprondict:
	if word in words:
		continue
	else:
		words.add(word)
		prons = cmuprondict[word]
		newprons = []
		for pron in prons:
			newpron = []
			for phone in pron:
				newphone = phone.lower().strip('012') # omit stress markers
				newpron.append(newphone)
			newprons.append(newpron)
		if len(newprons) == 1:
			entry = '{} {}'.format(word, ' '.join(newprons[0]))
		else:
			entry_list = ['{} {}'.format(word, ' '.join(pron)) for pron in newprons]
			entry = '\n'.join(entry_list)
		entries.append(entry)

for e in sorted(entries):
	big_lexfile.write('{}\n'.format(e))
big_lexfile.close()





