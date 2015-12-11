import nltk, string
from nltk.corpus import cmudict

cmu = cmudict.dict()

with open('broadcast_oov.txt', 'r') as infile:
	revised_oov_list = []
	for line in infile.readlines():
		word = line.strip(' !@#*()-+{}[]\'\n\"')
		wordlist = word.split('-')
		for word in wordlist:
			if word not in cmu and word != '':
				revised_oov_list.append(word)
			if '{' in word:
				print word
	outfile = open('revised_broadcast_oov.txt', 'w')
	for word in sorted(revised_oov_list):
		outfile.write('{}\n'.format(word))
	outfile.close()
