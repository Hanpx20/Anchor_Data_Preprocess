#!/usr/bin/env bash

# $BASE_DIR: The dir where you put the data and ckpts
# input_file: ${BASE_DIR}/web_data/web_raw/anchor.tsv

WEB_DATA_DIR=${BASE_DIR}/web_data

if [ $# -gt 0 ]; then
    IN_FILE=${WEB_DATA_DIR}/raw/"$1"
else
    # 如果没有额外命令行参数，则使用默认值
    IN_FILE=${WEB_DATA_DIR}/raw/inlink.jsonl
fi

OUT_DIR=${WEB_DATA_DIR}/anchor
STAT_DIR=${WEB_DATA_DIR}/stat
set +e
mkdir -p $OUT_DIR
mkdir $STAT_DIR
set -e
echo "filter out header/footer anchors AND in-domain anchors"
pv $IN_FILE | python filter_by_format_and_clean.py $OUT_DIR/anchor_step1.tsv $STAT_DIR

echo "filter out anchors by keywords and cut anchors with length >= MAXLEN (64 by default)"
pv $OUT_DIR/anchor_step1.tsv | python filter_by_keywords_and_len.py $OUT_DIR/url2anchor_step2.pkl $STAT_DIR
