"""
TODO:
Get UFA dicts
Get UFA words (from trans)
Get ATCOSIM words (from wordlist)
Is it cheating to look at all files?

Modify UFA prons?
Look up other words in CMU
Modify CMU prons
CMU phones are proper subset of UFA

Partial words?
Count how many words are from UFA
"""
import os, nltk, sys
from nltk.corpus import cmudict
cmuprondict = cmudict.dict()

class KaldiDict(object):
	def __init__(self):
		self.lexicon = {} #key: word, value: list of phone lists
	def add_ufa(self, dict_fpath):
		with open(dict_fpath, 'r') as dictfile:
			for line in dictfile.readlines():
				line = line.replace('-NX', '-NG')
				lineList = line.split()
				word = lineList[0][1:].lower() #get rid of '>' char
				prons = [pron.lower().split('-') for pron in lineList[1:]]
				self.lexicon[word] = prons

	def trans_to_wordlist(self, trans_fpath):
		wordlist = []
		with open(trans_fpath, 'r') as transfile:
			for line in transfile.readlines():
				words = line.lower().split()[:-1] #ignore tag at the end
				wordlist.extend(words)
		return set(wordlist)
		
	def file_to_wordlist(self, wordlist_fpath):
		wordlist = []
		with open(wordlist_fpath, 'r') as wordfile:
			for line in wordfile.readlines():
				if line[0].isalpha():
					wordlist.append(line.lower().strip())
		return set(wordlist)

	def add_wordlist(self, wordlist):
		for w in wordlist:
			if w in self.lexicon or '=' in w:
				continue
			else:
				self.lexicon[w] = self.cmu_lookup(w)			
					
	def cmu_lookup(self, word):
		if word in cmuprondict:
			prons = cmuprondict[word]
			newprons = []
			for pron in prons:
				newpron = []
				for phone in pron:
					newphone = phone.lower().strip('012') # omit stress markers
					newpron.append(newphone)
				newprons.append(newpron)
			return newprons
		else:
			return 'OOV_WORD'

	def write_dict(self, fname):
		with open(fname, 'w') as dictfile:
			for w in sorted(self.lexicon):
				if len(self.lexicon[w]) == 1 and self.lexicon[w] != 'OOV_WORD':
					dictfile.write('{} {}\n'.format(w, ' '.join(self.lexicon[w][0])))
				elif self.lexicon[w] == 'OOV_WORD':
					dictfile.write('{} OOV_WORD\n'.format(w))
				else:
					entry_list = ['{} {}'.format(w, ' '.join(pron)) for pron in self.lexicon[w]]
					dictfile.write('\n'.join(entry_list)+'\n')
				
	def write_oovlist(self, fname):
		with open(fname, 'w') as oovfile:
			oov_list = [w for w in self.lexicon if self.lexicon[w]=='OOV_WORD']
			for w in sorted(oov_list):
				oovfile.write('{}\n'.format(w))

if __name__ == '__main__':
	#adjust according to your own paths
	ufatrans_fpath = '/Users/meitalsinger/Desktop/ASR/Kaldi_project/UFA_DE/trans/UFA_DE.trans' #Tali's path
	ufadicts_dirpath = '/Users/meitalsinger/Desktop/ASR/Kaldi_project/grammar_3.16.9.4' #Tali's path
	atc_fpath = '/Users/meitalsinger/Desktop/ASR/atcosim/TXTdata/wordlist.txt'

	lexicon = KaldiDict()

	#add data from .hd files
	ufapaths = ['{}/{}'.format(ufadicts_dirpath, f) for f in os.listdir(ufadicts_dirpath) if f.endswith('.hd')]
	for f in ufapaths:
		lexicon.add_ufa(f)
	ufa_total = len(lexicon.lexicon)
	print 'UFA words: {}'.format(ufa_total)

	#get other words from UFA transcripts
	ufa_list = lexicon.trans_to_wordlist(ufatrans_fpath)
	lexicon.add_wordlist(ufa_list)
	#get atc words
	atc_list = lexicon.file_to_wordlist(atc_fpath)
	lexicon.add_wordlist(atc_list)

	total = len(lexicon.lexicon)
	print 'Total words: {}'.format(total)

	lexicon.write_dict('lexicon.txt')
	lexicon.write_oovlist('oov.txt')
