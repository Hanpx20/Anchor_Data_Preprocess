set -e

export BASE_DIR=/bos/tmp6/peixuanh #Outut Directory
export CLUEWEB_DIR=/bos/tmp6/ClueWeb22_A #Path of ClueWeb

mkdir -p ${BASE_DIR}/web_data/raw
mkdir -p ${BASE_DIR}/web_data/res
touch $BASE_DIR/web_data/res/index_register.txt
sleep 1

cd formating
source reset.sh
cd ..

group_id=3
folder_lo=0
folder_hi=1
lo=${1:-0}
hi=${2:-4}

#01

for ((t=$folder_lo; t<$folder_hi; t++))
do
    for ((i=$lo; i<$hi; i++))
    do 
        groupid=$(printf "%02d" "$group_id")
        folderid=$groupid$(printf "%02d" "$t")
        fileid=$(printf "%02d" "$i")
        echo -e "\033[33mWorking on en$folderid-$fileid\033[0m"

        cp $CLUEWEB_DIR/txt/en/en$groupid/en$folderid/en$folderid-$fileid.json.gz ${BASE_DIR}/web_data/raw
        gzip -d -c ${BASE_DIR}/web_data/raw/en$folderid-$fileid.json.gz > ${BASE_DIR}/web_data/raw/txt.jsonl
        rm  ${BASE_DIR}/web_data/raw/en$folderid-$fileid.json.gz
        cp $CLUEWEB_DIR/inlink/en/en$groupid/en$folderid/en$folderid-$fileid.json.gz ${BASE_DIR}/web_data/raw
        gzip -d -c ${BASE_DIR}/web_data/raw/en$folderid-$fileid.json.gz > ${BASE_DIR}/web_data/raw/inlink.jsonl
        rm  ${BASE_DIR}/web_data/raw/en$folderid-$fileid.json.gz

        cd anchor_filtering
        source filter_rules.sh 
        source filter_classifier.sh 0.25

        cd ../doc_preprocessing
        source clueweb.sh 
        source clean_and_split.sh 

        cd ../anchor_filtering
        source sample_anchors.sh

        cd ../formating
        source format.sh

        cd ..
        set +e
        rm $BASE_DIR/web_data/anchor/*
        rm $BASE_DIR/web_data/corpus/*
        rm $BASE_DIR/web_data/raw/*
        rm $BASE_DIR/web_data/stat/*
        rm $BASE_DIR/web_data/res/*.tmp.tsv
        rm $BASE_DIR/web_data/res/*.clean
        set -e
    done
done

