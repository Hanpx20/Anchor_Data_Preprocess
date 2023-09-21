import torch
from torch.utils.data import TensorDataset, DataLoader, RandomSampler, SequentialSampler
from transformers import BertTokenizer, BertForSequenceClassification
from sklearn.model_selection import train_test_split
from utils import *
import multiprocessing
import numpy as np
import pickle
from datasets import load_dataset, load_from_disk, Dataset

from tabulate import tabulate
from tqdm import tqdm
import random
import sys
import argparse
import os

NUM_EPOCHS=3
MAX_LEN=32

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--neg_num', default=300, type=int, help='num of negs used in training')
    parser.add_argument('--input_queries_file', help='queries to rank and filter', default='url2anchor_step2.pkl')
    parser.add_argument('--output_file', help='the output file', default='url2anchor_final.pkl')
    parser.add_argument('--ratio', default=0.25, type=float)
    parser.add_argument('--model_path', default = "", help="Use a trained model to skip training section")
    parser.add_argument('--save', action="store_true")
    args = parser.parse_args()

    global THRESH
    THRESH = args.ratio

    random.seed(1)
    
    neg_num = args.neg_num
    # generate training data with k negs in total 
    file_path = 'data/'
    train_data = []
    with open(file_path + 'train_pos.txt', 'r') as fin:
        for line in fin:
            q = line.strip().split(':')[1]
            train_data.append((q,1))

    neg_file = file_path + 'train_neg.txt'
    with open(neg_file, 'r') as fin:
        for i,line in enumerate(fin):
            q = line.strip()
            train_data.append((q,0))
            if i > neg_num:
                break

    random.shuffle(train_data)
    text =  np.array([x[0] for x in train_data])
    labels =  np.array([x[1] for x in train_data])

    tokenizer = BertTokenizer.from_pretrained(
        'bert-base-uncased',
        do_lower_case = True
    )

    token_id = []
    attention_masks = []

    for sample in text:
        encoding_dict = preprocessing(sample, tokenizer)
        token_id.append(encoding_dict['input_ids']) 
        attention_masks.append(encoding_dict['attention_mask'])

    token_id = torch.cat(token_id, dim = 0)
    attention_masks = torch.cat(attention_masks, dim = 0)
    labels = torch.tensor(labels)

    val_ratio = 0.1
    # Recommended batch size: 16, 32. See: https://arxiv.org/pdf/1810.04805.pdf
    batch_size = 8
    val_batch_size = 16

    # Indices of the train and validation splits stratified by labels
    train_idx, val_idx = train_test_split(
        np.arange(len(labels)),
        test_size = val_ratio,
        shuffle = True,
        stratify = labels,
        random_state = 1
    )

    data_path = '/'.join(args.input_queries_file.split('/')[:-1])
    if os.path.exists(data_path + '/query_set.hf'):
        pass
    else:
        print('Creating anchor dataset..')
        anchors = set()
        url2anchor = pickle.load(open(args.input_queries_file, 'rb'))
        for u in tqdm(url2anchor):
            for a in url2anchor[u]:
                anchors.add(a)
                
        test_text_dataset = Dataset.from_dict({'text':list(anchors)})
        # test_text_dataset = load_dataset('text', data_files=args.input_queries_file)['train']
        test_set = test_text_dataset.map(lambda x: tokenizer(x["text"], return_token_type_ids=False, padding='max_length', max_length=MAX_LEN, truncation=True), batched=True, batch_size=4096, num_proc=multiprocessing.cpu_count())
        #test_set.save_to_disk(data_path + '/query_set.hf')
        print('Anchor dataset loaded.')

    # Prepare DataLoader
    test_dataloader = DataLoader(
                test_set,
                sampler = SequentialSampler(test_set),
                batch_size = val_batch_size,
                num_workers=16,
                collate_fn=text_collate_fn,
            )

    # Load the BertForSequenceClassification model
    if args.model_path == "":
        model = BertForSequenceClassification.from_pretrained(
            'prajjwal1/bert-mini',
            num_labels = 2,
            output_attentions = False,
            output_hidden_states = False,
        )
    else:
        model = BertForSequenceClassification.from_pretrained(args.model_path)

    # Run on GPU
    if torch.cuda.is_available():
        model.cuda()

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # Recommended number of epochs: 2, 3, 4. See: https://arxiv.org/pdf/1810.04805.pdf
    if args.model_path == "":
        pass
    else:
        test_logits = []
        for batch in tqdm(test_dataloader):
            batch = tuple(t.to(device) for t in batch)
            b_input_ids, b_input_mask = batch
            with torch.no_grad():
                # Forward pass
                eval_output = model(b_input_ids, 
                                    token_type_ids = None, 
                                    attention_mask = b_input_mask)
            logits = eval_output.logits.detach().cpu().numpy() # for each sample, logits = [score_label0, score_label1]
            batch_logits = logits[:,1].tolist()
            test_logits.extend(batch_logits)
            
            
            
    # save rankings to file 
    sorted_idx = np.argsort( -np.array(test_logits) )
    #sorted_idx = np.argsort( np.array(test_logits) ) #选最差的！
    selected_num = int(len(sorted_idx) * THRESH)
    selected_idx = sorted_idx[:selected_num].tolist()
    selected_query_subset = set([test_set[i]['text'] for i in selected_idx])
    # with open(args.output_file, 'wb') as fout:
    #     pickle.dump(selected_query_subset, fout)
    
    new_url2anchor = {}
    for u in url2anchor:
        new_a = [a for a in url2anchor[u] if a in selected_query_subset]
        if len(new_a) > 0:
            new_url2anchor[u] = new_a 
            
    with open(args.output_file, 'wb') as fout:
        pickle.dump(new_url2anchor, fout)