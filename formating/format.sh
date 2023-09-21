
COR_FILE=$BASE_DIR/web_data/raw/txt.jsonl
ANCHOR_FILE=$BASE_DIR/web_data/res/train.tok.clean
OUT_DIR=$BASE_DIR/web_data/res

echo "Formating Data to corpus,query,qrel"
python format.py $COR_FILE $ANCHOR_FILE $OUT_DIR cat