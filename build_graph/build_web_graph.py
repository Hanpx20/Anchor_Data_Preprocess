import json
import pickle 
import time
from joblib import load
import sys
start_time = time.time()


filter_out_keyword_set = {
    'website',
    'official website',
    'original',
    'view website',
    'visit website',
    'visit our website',
    'visit website',
    'visit site',
    'home',
    'home page',
    'homepage',
    'about',
    'about us',
    'here',
    'this',
    'this article',
    'this page',
    'click here',
    'link',
    'source link',
    'offsite link',
    'this link',
    'more',
    'more info',
    'more information',
    'view more',
    'learn more',
    'read more',
    'see more',
    'find out more',
    'english',
    'en',
    'download',
    'save',
    'login',
    'sign in',
    'sign up',
    'register',
    'reply',
}

def get_domain(link):
    if 'https://' in link:
        domain = link[8:].split('/')[0]
    elif 'http://' in link:
        domain = link[7:].split('/')[0]
    else:
        domain = ''

    return domain 







if len(sys.argv) > 1:
    BASE_DIR = sys.argv[1]
else:
    BASE_DIR = "/home/peixuanh/Graph_Data"



url_set = pickle.load(open(BASE_DIR + "/url_set.pkl", "rb"))
url_to_id = pickle.load(open(BASE_DIR + "/url_to_id.pkl", "rb"))
#query_set = pickle.load(open(BASE_DIR + "/query_set.pkl", "rb"))


triples = []

with open(BASE_DIR + "/inlink_all.jsonl", "r") as fin:
    for line in fin:
        X = json.loads(line)
        if X['url'] not in url_set:
            continue
        tar_id = url_to_id[X['url']]
        # if tar_id >= 8098771:
        #     continue
        
        cnt = 0
        for instance in X['anchors']:
            if instance[0] in url_set:
                from_id = url_to_id[instance[0]]
                
                '''Filtering'''
                # if cnt >= 20:
                #     break
                # if from_id >= 8098771:
                #     continue

                if instance[3] != '' and instance[3] != '0':
                    continue
                if not get_domain(instance[0]) or get_domain(X['url']) == get_domain(instance[0]):
                    continue
                if len(instance[2].split()) > 64:
                    continue
                if instance[2].replace(' ','').lower() in filter_out_keyword_set:
                    continue
                if from_id == tar_id:
                    continue
                
                cnt += 1
                triples.append((from_id, tar_id))

print(len(triples))


with open(BASE_DIR + "/triples.tsv", "w") as file:
    for item in triples:
        file.write(f"{item[0]}\t{item[1]}\n")