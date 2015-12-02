#! /bin/bash

if [[ -z $KALDI ]]; then
    KALDI=/PATH/TO/KALDI
fi

export PATH=$(pwd)/utils/:\
$KALDI/src/bin:\
$KALDI/tools/openfst/bin:\
$KALDI/tools/sph2pipe_v2.5/sph2pipe:\
$KALDI/src/fstbin/:\
$KALDI/src/gmmbin/:\
$KALDI/src/featbin/:\
$KALDI/src/lm/:\
$KALDI/src/sgmmbin/:\
$KALDI/src/fgmmbin/:\
$KALDI/src/latbin/:\
$KALDI:\
$PATH
export LC_ALL=C
