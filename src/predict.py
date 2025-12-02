import re
from src.postprocessing import post_process

INTAHA = r'\s+ا\s*هـ?\s+'

def predict(chunked_lines, unk_list, xo_list, chunked_indices, xo_indices):
    
    
    # extract features
    # predict over all chunked indices
    # recover
    # TODO: remove this
    result_lines = []

    final_results = post_process(result_lines, unk_list, xo_list, chunked_indices, xo_indices)
    return result_lines