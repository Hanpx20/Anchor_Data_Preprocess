from tqdm import tqdm
import pickle
CORPUS_PATH = "/bos/tmp6/peixuanh/corpus.tsv" #corpus path

query_set = set()
with open("/home/peixuanh/Graph_Data/queries.train.tsv", "r") as file: #query path
    for line in file:
        X = line.split('\t')
        query_set.add(X[0])
pickle.dump(query_set, open("/home/peixuanh/Graph_Data/query_set.pkl", "wb"))   

url_set = set()
url_to_id = dict()
with open(CORPUS_PATH, "r") as fin:
    for line in tqdm(fin):
        X = line.split('\t')
        url_set.add(X[-1][:-1]) # \n
        url_to_id[X[-1][:-1]] = (int)(X[0])


pickle.dump(url_set, open("/home/peixuanh/Graph_Data/url_set.pkl", "wb"))
pickle.dump(url_to_id, open("/home/peixuanh/Graph_Data/url_to_id.pkl", "wb"))
        

