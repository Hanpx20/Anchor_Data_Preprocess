# $BASE_DIR: The dir where you put the data and ckpts
# input_file: ${BASE_DIR}/web_data/web_raw/anchor.tsv

WEB_DATA_DIR=${BASE_DIR}/web_data

STEP2_DIR=${WEB_DATA_DIR}/anchor
#cp ${STEP2_DIR}/url2anchor_step2.pkl ${STEP2_DIR}/url2anchor_final.pkl

python train.py \
    --input_queries_file ${STEP2_DIR}/url2anchor_step2.pkl \
    --output_file ${STEP2_DIR}/url2anchor_final.pkl \
    --ratio $1 \
    --model_path q_classifier
