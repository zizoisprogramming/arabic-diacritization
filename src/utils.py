import pickle
import json
import numpy as np
from dotenv import load_dotenv
import os
import torch


load_dotenv()

char2idx_path = os.getenv('char2idx_path')
idx2char_path = os.getenv('idx2char_path')
diacritic2id_path = os.getenv('diacritic2id_path')
arabic_letters_map = os.getenv('arabic_letters')
unk_list_path = os.getenv('unk_list_path')

def load_data_pickle(file_path):
    with open(file_path, 'rb') as f:
        X_raw, y_raw = pickle.load(f)
    X = []
    y = []

    for text_seq, label_seq in zip(X_raw, y_raw):
        x_ids = [c for c in text_seq]
        y_ids = [t for t in label_seq]

        X.append(x_ids)
        y.append(y_ids)

    return X, y

def get_diacritics_map():
    with open(diacritic2id_path, 'r', encoding='utf-8') as f:
        diacritic2id = json.load(f)
    idx2label = {v: k for k, v in diacritic2id.items()}

    return diacritic2id, idx2label

def get_char_map():
    with open(char2idx_path, 'r', encoding='utf-8') as f:
        char2idx = json.load(f)

    with open(idx2char_path, 'r', encoding='utf-8') as f:
        idx2char = json.load(f)

    return char2idx, idx2char


def get_tashkeel_sequence(new_tashkeel, index):
    return new_tashkeel[index]


def tokens_to_word_embeddings(tokens, embeddings):
    word_embeddings = []
    current_word_embs = []

    for token, emb in zip(tokens, embeddings):
        emb_tensor = torch.tensor(emb) if isinstance(emb, np.ndarray) else emb

        if token.startswith("##"):
            current_word_embs.append(emb_tensor)
        else:
            if current_word_embs:
                word_embeddings.append(torch.mean(torch.stack(current_word_embs), dim=0))
            current_word_embs = [emb_tensor]

    if current_word_embs:
        word_embeddings.append(torch.mean(torch.stack(current_word_embs), dim=0))

    return torch.stack(word_embeddings)


def get_arabic_characters():
    with open(arabic_letters_map, 'rb') as f:
        arabic_letters = pickle.load(f)
    return arabic_letters


def arabic_only(text):
    ARABIC_CHARS = get_arabic_characters()
    return "".join([char for char in text if char in ARABIC_CHARS or char == " "])