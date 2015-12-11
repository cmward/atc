#nonsilence phones
cat full_lexicon.txt | awk '{ for(n=2;n<=NF;n++){ phones[$n] = 1; }} END{for (p in phones) print p;}' | \
  grep -v sil > nonsilence_phones.txt  || exit 1;

#silence phones
echo sil > silence_phones.txt

#optional silence
echo sil > optional_silence.txt

#extra questions
echo -n > extra_questions.txt