import re
from utils import get_arabic_characters
import itertools

DIACRITICS_PATTERN = re.compile(r'[\u064B-\u0652]') 


def split_text_and_diacritics(text):

    letters = []
    labels = []
    
    i = 0
    while i < len(text):
        char = text[i]
        
        if DIACRITICS_PATTERN.match(char):
            if labels:
                labels[-1] += char
        else:
            letters.append(char)
            labels.append("") 
            
        i += 1
        
    return "".join(letters), labels

def reconstruct_text_window(chunks, overlaps):
    if not chunks:
        return ""
    
    reconstructed_parts = [chunks[0]]
    
    for chunk, ov in zip(chunks[1:], overlaps):
        reconstructed_parts.append(chunk[ov:])
        
    return "".join(reconstructed_parts)


def arabic_only_text_and_tashkeel(text, tashkeel):
    ARABIC_CHARS = get_arabic_characters()
    return "".join([char for char in text if char in ARABIC_CHARS or char == " "]), "".join([tashkeel[i] for i, char in enumerate(text) if char in ARABIC_CHARS or char == " "])

def post_process(all_text_chunks, all_overlaps, all_recovery, all_predicted):
    reconstructed = []
    final_tashkeel = []
    flat_tashkeel = list(itertools.chain.from_iterable(all_predicted))
    idx = 0
    
    for i in range(len(all_recovery)):
        res = ''

        curr_chunks = []
        curr_overlaps = []
        
        overlap_idx = 0 
        
        for j in range(len(all_recovery[i])):
            recovery_id = all_recovery[i][j]
            chunk = all_text_chunks[i][j]
            
            if recovery_id == 0:
                if curr_chunks:
                    res += reconstruct_text_window(curr_chunks, curr_overlaps)
                
                curr_chunks = [chunk]
                curr_overlaps = [] 
            
            else:
                curr_chunks.append(chunk)
                
                if overlap_idx < len(all_overlaps[i]):
                    curr_overlaps.append(all_overlaps[i][overlap_idx])
                    overlap_idx += 1

        if curr_chunks:
            res += reconstruct_text_window(curr_chunks, curr_overlaps)
        
        res, tashkeel = arabic_only_text_and_tashkeel(res, flat_tashkeel[idx:idx+len(res)])
        reconstructed.append(res)
        final_tashkeel.append(tashkeel)
        idx += len(res)
        
    return reconstructed, final_tashkeel