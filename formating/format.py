import sys
import json
import codecs
import re
import os

corpus_file = sys.argv[1]
anchor_file = sys.argv[2]
output_dir = sys.argv[3]
method = sys.argv[4]

assert method == "new" or method == "cat"

def out_file_name():
    return "tsv" if method == "new" else "tmp.tsv"


_ = open(f"{output_dir}/index_register.txt", "r").readlines()
d_ind = (int)(_[0])
q_ind = (int)(_[1])
print('-'*50)
print(d_ind)
print(q_ind)
print('-'*50)
def read_json_file(file_path):
    total_rows = 0
    rows = []
    with open(file_path, 'r') as file:
        for line in file:
            total_rows += 1
            rows.append(json.loads(line))
        return total_rows, rows

def split_title(document):
    if document.find('\n') != -1:
        title, content = document[:document.find('\n')], document[document.find('\n')+1:]
    else:
        title, content = document[:document.find(' ')], document[document.find(' ')+1:]
    title =  re.sub(r'[\n\r\t\a\b\f]', ' ', title)
    content = re.sub(r'[\n\r\t\a\b\f]', ' ', content)
    title = ' '.join(title.split()[:32])
    content = ' '.join(content.split()[:256])
    return title, content
    

_, corpus = read_json_file(corpus_file)
corpus_dict = {} #url->id
corpus_list = []

for index, instance in enumerate(corpus):
    url = instance['URL']
    url = url if '\n' not in url else url[:url.find('\n')]
    url = url.replace(' ', '')
    corpus_dict[url] = index
    title, content = split_title(instance['Clean-Text'])
    corpus_list.append([title, content, 0, url])


query_list = []
fout = open(f"{output_dir}/qrels.train.{out_file_name()}", "w")
with open(anchor_file, "r") as fin:
    queries = [entry.split('\n') for entry in fin.read().split('\n\n')]
    for entry in queries:
        if len(entry) < 6:
            continue
        try:
            doc_id = corpus_dict[entry[0][4:]]
        except:
            continue
        corpus_list[doc_id][2] = 1
        for query in entry[1:]:
            if query == '[PAD]':
                break
            query_list.append(query)
            fout.write(f"{len(query_list)-1+q_ind}\t0\t{doc_id+d_ind}\t1\n")

with open(f"{output_dir}/corpus.{out_file_name()}", "w") as fout:
    for index, entry in enumerate(corpus_list):
        if entry[2] == 1:
            fout.write(f"{index+d_ind}\t{entry[0]}\t{entry[1]}\t{entry[3]}\n")

with open(f"{output_dir}/queries.train.{out_file_name()}", "w") as fout:
    for index, query in enumerate(query_list):
        fout.write(f"{index+q_ind}\t{query}\n")
        
with open(f"{output_dir}/index_register.txt", "w") as fout:
    fout.write(f"{len(corpus_list)+d_ind}\n{len(query_list)+q_ind}\n")

if method == "cat":
    os.system(f"cat {output_dir}/corpus.tmp.tsv >> {output_dir}/corpus.tsv")
    os.system(f"cat {output_dir}/queries.train.tmp.tsv >> {output_dir}/queries.train.tsv")
    os.system(f"cat {output_dir}/qrels.train.tmp.tsv >> {output_dir}/qrels.train.tsv")