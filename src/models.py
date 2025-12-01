from transformers import AutoTokenizer, AutoModel
from arabert.preprocess import ArabertPreprocessor
import torch
import numpy as np
from dotenv import load_dotenv
import os
from src.utils import get_char_map
load_dotenv()


arabert_model_name = "aubmindlab/bert-base-arabertv02"
bert_tokenizer = AutoTokenizer.from_pretrained(arabert_model_name)
bert_model = AutoModel.from_pretrained(arabert_model_name)
bert_model.eval()
arabert_prep = ArabertPreprocessor(model_name=arabert_model_name)


char_embeddings_path = os.getenv('char_embeddings_path')
custom_char_embedding = np.load(char_embeddings_path)


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def get_arabert_embeddings(sentence: str):
    
    tokens = bert_tokenizer(sentence, return_tensors="pt", truncation=True, padding=True)
    tokens = {k: v.to(device) for k, v in tokens.items()}

    with torch.no_grad():
        output = bert_model(**tokens)

    emb = output.last_hidden_state.squeeze(0).cpu()
    token_list = bert_tokenizer.convert_ids_to_tokens(tokens["input_ids"][0])

    return emb.numpy(), token_list



def extract_custom_char_embeddings(char):   
    char2idx, _ = get_char_map()
    return custom_char_embedding[char2idx[char]]