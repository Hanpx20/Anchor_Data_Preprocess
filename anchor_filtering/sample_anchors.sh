#!/usr/bin/env bash
# $BASE_DIR: The dir where you put the data and ckpts
# input_file: ${BASE_DIR}/web_data/web_raw/anchor.tsv
WEB_DATA_DIR=${BASE_DIR}/web_data

INPUT_DIR=${WEB_DATA_DIR}/raw
STAT_DIR=$WEB_DATA_DIR/stat

WEB_CORPUS_DIR=${WEB_DATA_DIR}/corpus
RES_DIR=${WEB_DATA_DIR}/res
ANCHOR_SUBSET_FILE=${WEB_DATA_DIR}/anchor/url2anchor_final.pkl
set +e
mkdir -p $RES_DIR
set -e
train_file=${WEB_CORPUS_DIR}/corpus.train_url
valid_file=${WEB_CORPUS_DIR}/corpus.valid_url


pv $train_file | python sample_anchors.py $ANCHOR_SUBSET_FILE $RES_DIR/train.tok.clean $STAT_DIR train
pv $valid_file | python sample_anchors.py $ANCHOR_SUBSET_FILE $RES_DIR/valid.tok.clean $STAT_DIR valid
