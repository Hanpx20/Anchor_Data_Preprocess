# $BASE_DIR: The dir where you put the data and ckpts
# input_file: ${BASE_DIR}/web_data/web_raw/web_corpus.tsv


WEB_DATA_DIR=${BASE_DIR}/web_data
URL_FILE=${WEB_DATA_DIR}/anchor/url2anchor_final.pkl
OUT_DIR=$WEB_DATA_DIR/corpus
set +e
mkdir $OUT_DIR
set -e
if [ $# -gt 0 ]; then
    IN_FILE=${WEB_DATA_DIR}/raw/"$1"
else
    # 如果没有额外命令行参数，则使用默认值
    IN_FILE=${WEB_DATA_DIR}/raw/txt.jsonl
fi

python WebExtractor.py $IN_FILE --keep_url --url_subset_file ${URL_FILE} -b 30G -q -o - > $OUT_DIR/corpus_step1.txt

