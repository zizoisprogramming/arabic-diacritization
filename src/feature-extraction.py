# !pip install -q transformers arabert preprocess
# !pip install -q stanza
# !pip install -q gensim
# !pip install -q flair
# !pip install -q lang-trans

import torch
import torch.nn as nn

import stanza

import numpy as np
import pickle
import os
from tqdm import tqdm
from gensim.models import FastText
from flair.data import Sentence
from flair.embeddings import CharacterEmbeddings, StackedEmbeddings
from lang_trans.arabic import buckwalter
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
import pandas as pd
import json
from dotenv import load_dotenv
from src.utils import load_data_pickle, get_tashkeel_sequence, remove_pads, tokens_to_word_embeddings
from src.models import get_arabert_embeddings, extract_custom_char_embeddings

load_dotenv()

dataset_path = os.getenv('dataset_path')

sentences, tashkeel_sequences = load_data_pickle(dataset_path)
new_sentences, new_tashkeel = remove_pads(sentences, tashkeel_sequences)

def zizo_features(sentence: str,
                  sent_index: int,
                  arabert_model=None,
                  arabert_tokenizer=None,
                  fasttext_model=None):

    sentence_vec = []
    
    tashkeel = get_tashkeel_sequence(sent_index) 

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

    return sentence_vec, tashkeel