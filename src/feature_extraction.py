# !pip install -q transformers arabert preprocess
# !pip install -q stanza
# !pip install -q gensim
# !pip install -q flair
# !pip install -q lang-trans

import torch
import torch.nn as nn


import numpy as np
import pickle
import os
from tqdm import tqdm
import pandas as pd
import json
from dotenv import load_dotenv
from utils import load_data_pickle, get_tashkeel_sequence, tokens_to_word_embeddings
from models import get_arabert_embeddings, extract_custom_char_embeddings, bert_model, bert_tokenizer

load_dotenv()

dataset_path = os.getenv('dataset_path')

sentences, tashkeel_sequences = load_data_pickle(dataset_path)

def zizo_features(sentence: str):

    sentence_vec = []
    
    arabert_emb, tokens = get_arabert_embeddings(sentence)
    final_arabert_emb = tokens_to_word_embeddings(tokens, arabert_emb)
    
    words_raw = sentence.split() 
    word_idx = 0          
    char_in_word_idx = 0 
    
    emb_dim = final_arabert_emb[0].shape[0]

    for i, char in enumerate(sentence):
        
        char_emb = extract_custom_char_embeddings(char)
        char_emb_array = np.array(char_emb).flatten()
        
        if char == ' ':
            bert_vec = np.zeros(emb_dim) 
            
        else:
            bert_vec = final_arabert_emb[word_idx]
            if isinstance(bert_vec, torch.Tensor):
                bert_vec = bert_vec.numpy()
                
            char_in_word_idx += 1
            
            if char_in_word_idx == len(words_raw[word_idx]):
                word_idx += 1        
                char_in_word_idx = 0 
        
        char_vector = np.concatenate([bert_vec, char_emb_array])
        sentence_vec.append(char_vector)

    return sentence_vec


def extract_features(sentences):

    buffer_features = []
    for i in tqdm(range(len(sentences)), total=len(sentences), desc="extracting features"):
    
        sent = sentences[i]

        features = zizo_features("".join(sent), i, bert_model, bert_tokenizer)

        buffer_features.extend(features)

    return np.array(buffer_features, dtype=np.float16)