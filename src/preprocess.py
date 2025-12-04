import re


numeric_pattern = r"\(\s*\d+\s*/\s*\d+\s*\)"
english = r"[a-zA-Z]"
numbers = r"\s*\d+\s*"
numering_items = r"\s*\d+\s*[-]\s*"
empty_brackets = r'\(\s*\)|\[\s*\]|\{\s*\}|<<\s*>>|"\s*"|\'\s*\''

def clean_punctuation_sequence(text):
    collapsible = re.escape(".,:;!?'\"/،؛؟")
    pattern = rf"([{collapsible}])(?:\s*\1)+"

    return re.sub(pattern, r"\1", text)

def remove_unbalanced_brackets(text):
    pair_map = {')': '(', '}': '{', ']': '[', '>':'<', '»': '«', '"':'"', "'":"'"}
    openers = set(['(', '{', '[', '<', '«', '"', "'"])
    
    stack = [] 
    indices_to_remove = set()

    for i, char in enumerate(text):
        if char in openers:
            stack.append((char, i))
        
        elif char in pair_map:
            if stack:
                last_opener, _ = stack[-1]
                if last_opener == pair_map[char]:
                    stack.pop()
                else:
                    indices_to_remove.add(i)
            else:
                indices_to_remove.add(i)

    for char, index in stack:
        indices_to_remove.add(index)

    return "".join([char for i, char in enumerate(text) if i not in indices_to_remove])


def initial_process(line):
    res = re.sub(numering_items, '', line)
    res = re.sub(numeric_pattern, '', res)
    res = re.sub(english, ' ', res)
    res = re.sub(numbers, '', res)
    res = re.sub(empty_brackets, '', res)
    res = re.sub(',', '،', res)
    res = re.sub(';', '؛', res)
    res = re.sub(r'\?', '؟', res)
    res = re.sub(r'/', '', res)
    res = re.sub(r'\*', '', res)
    res = re.sub(r'–', '-', res)
    res = res.replace('\u200f', '')
    

    res = clean_punctuation_sequence(res)

    res = remove_unbalanced_brackets(res)

    res = re.sub(r"\s+", " ", res).strip()

    return res


def split_citations_raw(line):
    qal_list = [
        "قال", "قالت", "قالوا", "قلت", "قلنا",
        "أقول", "يقول", "يقولون", "قيل", "يقال"
    ]

    qal_regex = "|".join(qal_list)

    qal_with_colon = rf"(?:{qal_regex})\s*[:：]"

    
    qawloho_regex = r"(?:و|ف)?قول(?:ه)?(?:\s*تعالى)?"

    trigger = rf"({qal_with_colon}|{qawloho_regex})"

    final_lines = []
    matches = list(re.finditer(trigger, line))
    
    if not matches:
        final_lines.append(line.strip())
    else:
        last_idx = 0
        for m in matches:
            start = m.start()
            if line[last_idx:start]:
                final_lines.append(line[last_idx:start])
            last_idx = start
        
        final_lines.append(line[last_idx:])

    return final_lines

def slide_window_raw(text, overlap=50, max_len=807):
    if len(text) <= max_len:
        return [text], []
    
    chunks = []
    overlaps = []
    
    chunks.append(text[:max_len])
    
    current_start = 0
    text_len = len(text)
    
    while True:
        ideal_stride = max_len - overlap
        
        ideal_next_start = current_start + ideal_stride
        
        if ideal_next_start >= text_len:
            break

        found_next_start = -1
        
        search_limit = current_start  
        
        for i in range(ideal_next_start, search_limit, -1):
            if i < text_len and text[i] == ' ':
                found_next_start = i + 1 
                break
        
        if found_next_start == -1:
            found_next_start = ideal_next_start
            
        
        actual_overlap = (current_start + max_len) - found_next_start
        
        if actual_overlap < 0:
            actual_overlap = 0

        next_chunk = text[found_next_start : found_next_start + max_len]
        
        chunks.append(next_chunk)
        overlaps.append(actual_overlap)
        
        current_start = found_next_start
        
        if current_start + max_len >= text_len:
            break
            
    return chunks, overlaps

def prepare_for_predict():
    all_text_chunks = []
    all_recovery = []
    all_overlaps = [] 
    length = 0
    assertions = []
    
    with open('/home/zizo/Documents/NLP/Project/data/val.txt', "r", encoding="utf-8") as file:
        
        for line in file:
            length += 1

            # line, _ = split_text_and_diacritics(line) # only for Val not test
            recovery = []
            curr_chunks = []
            curr_overlaps = [] 
            
            cleaned = initial_process(line.strip())
            assertions.append(cleaned)
            
            raw_segments = split_citations_raw(cleaned)

            for seg in raw_segments:
                t_chunks, t_overlaps = slide_window_raw(seg, overlap=50, max_len=807)
                
                for i, chunk in enumerate(t_chunks):
                    recovery.append(i)
                    curr_chunks.append(chunk)
                
               
                curr_overlaps.extend(t_overlaps)

            all_recovery.append(recovery)
            all_text_chunks.append(curr_chunks)
            all_overlaps.append(curr_overlaps) 
            
    print(f"Generated {len(all_text_chunks)} chunks.")
    return all_text_chunks, all_overlaps, all_recovery, length, assertions