import gensim
from gensim.models import Word2Vec
import re
def modeltrain():
    input_file = '/Users/emil07/Desktop/SUMRES/output.txt'
    output_model = '/Users/emil07/Desktop/SUMRES/model01.bin'

    sentences = []
    with open(input_file, 'r') as file:
        for line in file:
            sentences.append(line.split())

    # Train Word2Vec model
    word2vec_model = Word2Vec(sentences, vector_size=100, window=5, min_count=1, workers=4)
    word2vec_model.train(sentences, total_examples=len(sentences), epochs=20)

    # Save Word2Vec model
    word2vec_model.save(output_model)
