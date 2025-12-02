import re
from utils import get_arabic_characters

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

def recover(result_lines, unk_list, xo_list, chunked_indices, xo_indices):
    
    unk_iter = iter(unk_list)
    xo_iter = iter(xo_list)
    
    recovered_lines = [] 
    
    for i, line in enumerate(result_lines):
        
        indices = xo_indices[i]
        
        current_xo_texts = [next(xo_iter) for _ in range(len(indices))]
        
       
        repair_map = zip(reversed(indices), reversed(current_xo_texts))
        
        for idx, original_text in repair_map:
            if line[idx:idx+3] == ' ، ': 
                line = line[:idx] + original_text + line[idx+3:]
        
        def unk_replacer(match):
            try:
                return next(unk_iter)
            except StopIteration:
                return match.group(0)
                
        line = re.sub(r' \? ', unk_replacer, line)
        
        recovered_lines.append(line)

    final_documents = []
    
    for group in chunked_indices:
        merged_doc = ""
        for chunk_idx in group:
            merged_doc += recovered_lines[chunk_idx]
        final_documents.append(merged_doc)

    return final_documents


def post_process(test_results, unk_list, xo_list, chunked_indices, xo_indices):

    final_results = recover(test_results, unk_list, xo_list, chunked_indices, xo_indices)
    cleaned_test_results = []
    arabic_letters = get_arabic_characters()
    for line in final_results:
        cleaned_text, labels = split_text_and_diacritics(line)
        new_text = ''
        for i in range(len(cleaned_text)):
            if cleaned_text[i] in arabic_letters or cleaned_text[i] == ' ': # TODO: ask omar
                new_text += cleaned_text[i] + labels[i]
            

        cleaned_test_results.append(new_text)

    return cleaned_test_results