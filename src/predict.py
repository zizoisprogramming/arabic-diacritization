import re
from postprocessing import post_process
from preprocess import prepare_for_predict
from feature_extraction import extract_features
import tensorflow as tf

INTAHA = r'\s+ا\s*هـ?\s+'
BATCH_SIZE = 32
PADDING_INPUT = -9999
INPUT_DIM = 1024

def predict(chunked_lines):
    
    all_text_chunks, all_overlaps, all_recovery, length, assertions = prepare_for_predict()
    
    all_features = extract_features(all_text_chunks)

    all_sentence_lengths = [len(s) for s in all_text_chunks]

    def test_set_generator(all_sentence_lengths, offset=0):
        for i in range(offset, len(all_sentence_lengths)):
            yield all_features[i], [all_sentence_lengths[i]]

    test_dataset = tf.data.Dataset.from_generator(
            lambda: test_set_generator(all_sentence_lengths, offset=0),
            output_signature=(
                tf.TensorSpec(shape=(None, INPUT_DIM), dtype=tf.float32),
                tf.TensorSpec(shape=(None, 1), dtype=tf.int32)
            )
        ).padded_batch(BATCH_SIZE, padding_values=(PADDING_INPUT, 15))
    return post_process(chunked_lines)