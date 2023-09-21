set -e
export BASE_DIR=/bos/tmp6/peixuanh/graph #Outut Directory
export CLUEWEB_DIR=/bos/tmp6/ClueWeb22_A #Path of ClueWeb

mkdir -p $BASE_DIR

group_id=3
folder_lo=0
folder_hi=1
lo=${1:-0}
hi=${2:-4}

#Remenber to set PATHs in build_map.py!
python build_graph/build_map.py

for ((t=$folder_lo; t<$folder_hi; t++))
do
    for ((i=$lo; i<$hi; i++))
    do 
        groupid=$(printf "%02d" "$group_id")
        folderid=$groupid$(printf "%02d" "$t")
        fileid=$(printf "%02d" "$i")

        echo -e "\033[33mWorking on en$folderid-$fileid\033[0m"
        
        cp $CLUEWEB_DIR/inlink/en/en$groupid/en$folderid/en$folderid-$fileid.json.gz ${BASE_DIR}
        gzip -d -c ${BASE_DIR}/en$folderid-$fileid.json.gz > ${BASE_DIR}/inlink.jsonl
        rm  ${BASE_DIR}/en$folderid-$fileid.json.gz
        cat ${BASE_DIR}/inlink.jsonl >> ${BASE_DIR}/inlink_all.jsonl
        rm ${BASE_DIR}/inlink.jsonl
    done
    python build_graph/build_web_graph.py ${BASE_DIR}
    cat ${BASE_DIR}/triples.tsv >> /bos/tmp6/peixuanh/triples_all_A.tsv
    rm ${BASE_DIR}/inlink_all.jsonl
    rm ${BASE_DIR}/triples.tsv
done
