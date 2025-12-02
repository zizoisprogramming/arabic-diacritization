import re
import pickle
from utils import save_list

numeric_pattern = r"\(\s*\d+\s*/\s*\d+\s*\)"
english = r"[a-zA-Z]"
numbers = r"\d+"
numering_items = r"\s*\d+\s*[-]\s*"
empty_brackets = r'\(\s*\)|\[\s*\]|\{\s*\}|<<\s*>>|"\s*"|\'\s*\''
stand_alone=r'(?<=\s|\^|\(|\[|\{)[^\(\)\[\]\{\}\.,،:;؛؟!\-](?=\s|$|\]|\)|\})'
UNK_CHAR = '?'

kawloho_pattern = r"(\s*قَوْلُهُ\s*)"
qala_variations = r"(?:قَالَ|قَالَتْ|قُلْت|قَالُوا|قُلْنَا|أَقُولُ)"
qala_variations = r"(?:قَالَ|قَالَتْ|قُلْت|قَالُوا|قُلْنَا|أَقُولُ)"
qala_pattern = rf"(\s*{qala_variations}\s*:)"

punctuation = [' ', '،', ':', '؛', '!', '؟', '"', "'", '«', '»', '(', ')', '[', ']', '{', '}', '-', '.']
DIACRITICS_PATTERN = re.compile(r'[\u064B-\u0652]')

unk_list = []
MAX_LEN = 807

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

def clean_punctuation_sequence(text):
    collapsible = re.escape(".,:;!?'\"/،؛؟")    
    pattern = rf"([{collapsible}])(?:\s*\1)+"
    
    return re.sub(pattern, r"\1", text)


# def separate_citations(citation_pattern, lines):
#     final_lines = []

#     for line in lines:
#         modified_line = re.sub(citation_pattern, r"\n\1", line)
        
#         parts = modified_line.split('\n')
        
#         for part in parts:
#             cleaned_part = part.strip()
#             if cleaned_part:
#                 final_lines.append(cleaned_part)
                
#     return final_lines

def split_citations(lines):
    qal_list = [
        "قَالَ","قَالَتْ","قَالُوا","قُلْت","قُلْنَا",
        "أَقُولُ","يَقُولُ","يَقُولُونَ","قِيلَ","يُقَالُ"
    ]
    
    def add_tashkeel(word):
        tashkeel = "[\u064B-\u065F]*"
        return "".join([c + tashkeel for c in word])
    
    qal_regex = "|".join([add_tashkeel(w) for w in qal_list])

    qal_with_colon = rf"(?:{qal_regex})\s*[:：]"

    tashkeel = "[\u064B-\u065F]*"
    qawloho_regex = rf"(?:وَ|فَ)?قَوْل{tashkeel}(?:ه{tashkeel}|هُ{tashkeel})?(?:\s*تَعَالَى)?"

    trigger = rf"({qal_with_colon}|{qawloho_regex})"

    final_lines = []
    for line in lines:
        matches = list(re.finditer(trigger, line))
        if not matches:
            final_lines.append(line.strip())
            continue
        
        last_idx = 0
        for m in matches:
            start = m.start()
            if line[last_idx:start].strip():
                final_lines.append(line[last_idx:start].strip())
            last_idx = start
        
        final_lines.append(line[last_idx:].strip())
        
    return final_lines

def process_and_capture(text):
    xo_list = []
    unk_list = []
    INTAHA = r'\s+ا\s*هـ?\s+'

    xo_list = [m.group(0) for m in re.finditer(INTAHA, text)]
    text = re.sub(INTAHA, ' x ', text)

    p_brackets = fr'\((\s*{stand_alone}\s*)+\)'
    for m in re.finditer(p_brackets, text):
        unk_list.append(m.group(0))
    text = re.sub(p_brackets, f' {UNK_CHAR} ', text)

    p_raw = fr'(\s*{stand_alone}\s*)+'
    for m in re.finditer(p_raw, text):
        unk_list.append(m.group(0))
    text = re.sub(p_raw, f' {UNK_CHAR} ', text)
    unk_list = [x for x in unk_list if x.strip() != '?']

    return text, unk_list, xo_list

def initial_process(lines):
    new_lines = []
    unk_list = []
    xo_list = []
    for line in lines:
        res = re.sub(numering_items, '', line)
        res = re.sub(numeric_pattern, '', res)
        res = re.sub(english, ' ', res)
        res = re.sub(numbers, '', res)
        res = re.sub(empty_brackets, '', res)
        res = re.sub(',', '،', res) 
        res = re.sub(';', '؛', res) 
        res = re.sub('?', '؟', res) 
        res, unk_list_local, xo_list_local = process_and_capture(res)
        res = re.sub(r'/', '', res) 
        res = re.sub(r'\*', '', res) 
        res = re.sub(r'–', '-', res) 
        res = res.replace('\u200f', '') 
        
        res = clean_punctuation_sequence(res)
        res = remove_unbalanced_brackets(res)
        
        res = re.sub(r"\s+", " ", res).strip()
        new_lines.append(res)
        
        unk_list.extend(unk_list_local)
        xo_list.extend(xo_list_local)

    return new_lines, unk_list, xo_list


def slide_window(text, overlap=50, max_len=200):
    if len(text) <= max_len:
        return [text], [0]
    
    text_chunks = []
    text_indices = []
    
    stride = max_len - overlap
    j = 0
    
    for i in range(0, len(text), stride):

        t_chunk = text[i : i + max_len]
        text_chunks.append(t_chunk)
        text_indices.append(j)
        j += 1
        
        if i + max_len >= len(text): 
            break
            
    return text_chunks , text_indices

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


def process_text(lines_text):
    new_lines, unk_list, xo_list = initial_process(lines_text)
    save_list(unk_list)
    save_list(xo_list)
    
    new_lines = split_citations(new_lines)
    new_lines = [remove_unbalanced_brackets(line) for line in new_lines]
    
    cleaned_text = []

    for line in new_lines:
        line = re.sub(r'\s+', ' ', line).strip()
        if not line.strip():
            continue
        
        cleaned_text.append(line)

    chunked_lines = []
    chunked_indices = []

    for new_line in cleaned_text:
        chunks, indices = slide_window(new_line, overlap=50, max_len=MAX_LEN)
        
        for chunk in chunks:
            chunked_lines.append(chunk)
            chunked_indices.append(indices)

    xo_indices = []
    processed_lines = []
    for line in chunked_lines:
        xo_indices.append([m.start() for m in re.finditer(' x ', line)])
        processed = re.sub(' x ', ' ، ', line)
        processed_lines.append(processed)

    return processed_lines, unk_list, xo_list, chunked_indices