"""
import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from numpy import zeros, array, mean
from scipy.spatial.distance import cosine
from gensim.models import Word2Vec, KeyedVectors



def calculate_similarity2(model, vectors1, vectors2):
    wordscore = []
    top_score = []
    for vector01 in vectors1:
        for vector02 in vectors2:
            if not (vector01 == np.zeros(model.vector_size)).all() and not (vector02 == np.zeros(model.vector_size)).all():
                wordscore.append(1 - cosine(vector01, vector02))
        if wordscore:
            wordscore.sort()
            top_score.append(wordscore[-1])
            wordscore.clear()
    if top_score:  # check if top_score is not empty
        print(f"The average of the scores is: {mean(top_score)}")
    else:
        print("No scores were calculated.")

def calculate_similarity(model, vectors1, vectors2):
    if vectors1 and vectors2:
        mean_vector1 = mean(array(vectors1), axis=0)
        mean_vector2 = mean(array(vectors2), axis=0)

        # calculate the cosine similarity between the mean vectors
        similarity = 1 - cosine(mean_vector1, mean_vector2)
        print(f"The similarity between the terms is {similarity}.")
    else:
        print("No vectors were calculated.")

# not something we actually need but I spend some time doing it so I feel bad taking it out
def display_closestwords_tsnescatterplot(model, word):
    arr = np.empty((0, 300), dtype='f')
    word_labels = [word]

    # get close words
    close_words = model.similar_by_word(word)

    # add the vector for each of the closest words to the array
    arr = np.append(arr, np.array([model[word]]), axis=0)
    for wrd_score in close_words:
        wrd_vector = model[wrd_score[0]]
        word_labels.append(wrd_score[0])
        arr = np.append(arr, np.array([wrd_vector]), axis=0)

    # find tsne coords for 2 dimensions
    tsne = TSNE(n_components=2, random_state=0)
    np.set_printoptions(suppress=True)
    Y = tsne.fit_transform(arr)

    x_coords = Y[:, 0]
    y_coords = Y[:, 1]
    # display scatter plot
    plt.scatter(x_coords, y_coords)

    for label, x, y in zip(word_labels, x_coords, y_coords):
        plt.annotate(label, xy=(x, y), xytext=(0, 0), textcoords='offset points')
    plt.xlim(x_coords.min() + 0.00005, x_coords.max() + 0.00005)
    plt.ylim(y_coords.min() + 0.00005, y_coords.max() + 0.00005)
    plt.show()


def similarity():
    new_model_path = '/Users/emil07/Desktop/SNDAT/wikipedia-pubmed.model'
    loaded_model = KeyedVectors.load(new_model_path)
    print("Model loaded successfully!")
    term1 = input("Enter the first medical term: ").lower()
    term2 = input("Enter the second medical term: ").lower()

    # split the terms into individual words
    words1 = term1.split()
    words2 = term2.split()

    # check if the terms have the same tag
    if words1[-1] == words2[-1]:
        print("Both terms have the same tag.")
    else:
        print("The terms have different tags.")
    vectors1 = []
    for word1 in words1:
        try:
            vector1 = loaded_model[word1]
            vectors1.append(vector1)
        except KeyError:
            vector1 = zeros(loaded_model.vector_size)  # use a zero vector as the placeholder
            vectors1.append(vector1)
    vectors2 = []
    for word2 in words2:
        try:
            vector2 = loaded_model[word2]
            vectors2.append(vector2)
        except KeyError:
            vector2 = zeros(loaded_model.vector_size)
            vectors2.append(vector2)

    calculate_similarity(loaded_model, vectors1, vectors2)
    calculate_similarity2(loaded_model, vectors1,vectors2)
    # Test similarity
    """ # version 1
"""
    phrase = input("Enter a phrase: ").lower()
    words = phrase.split() # split the phrase into individual words
    for word in words:
        print(f"Finding similar words to '{word}'...")
        try:
            similar_words = word_vectors.most_similar(word)
            print(f"Similar words to '{word}':")
            for similar_word, score in similar_words:
                print(f"Word: {similar_word}, Similarity: {score}")
        except KeyError:
            print(f"The word '{word}' is not in the model's vocabulary.")
            similar_words = []
""" #checks the model for all similar words
import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from numpy import zeros, array, mean, unique
from scipy.spatial.distance import cosine
from gensim.models import KeyedVectors
import databse

# Some antonym pairs, this was supposed to make the difference in attribute justified but we're not using it anymore
ANTONYM_PAIRS = {
    "balanced": ["unbalanced"],
    "with": ["without"],
    "positive": ["negative"],
    "active": ["inactive"],
    "regular": ["irregular"],
    "normal": ["abnormal"],
}

# Loading the model I got from https://bio.nlplab.org/#word-vector-tools
new_model_path = '/Users/emil07/Desktop/SNDAT/wikipedia-pubmed.model'
loaded_model = KeyedVectors.load(new_model_path)
print("=== Model loaded successfully! ===\n")

"""Calculates the similarity score by taking the cosine similarity of each word vector of one term with the all other words of the other term
 then takes the max of that and adds to list. Then we take the average of that list with all the top scores and get the score"""
def avg_of_max_similarity(vectors1, vectors2, model):
    # Check which vector list is larger and swap if necessary
    if len(vectors2) > len(vectors1):
        vectors1, vectors2 = vectors2, vectors1

    wordscore = []
    top_score = []

    for vector01 in vectors1:
        for vector02 in vectors2:
            if not np.all(vector01 == np.zeros(loaded_model.vector_size)) and not np.all(vector02 == np.zeros(loaded_model.vector_size)):
                wordscore.append(1 - cosine(vector01, vector02))

        if wordscore:
            top_score.append(max(wordscore))
            wordscore.clear()

    # Round the result to two decimal places
    return round(np.mean(top_score), 2) if top_score else 0

"""The same as avg_of_max_similarity just that here we're doing it both ways"""
def calculate_bidirectional_similarity(model, vectors1, vectors2):
    def get_scores(vectors_a, vectors_b):
        scores = []
        for vector_a in vectors_a:
            word_scores = []
            for vector_b in vectors_b:
                if not np.all(vector_a == np.zeros(model.vector_size)) and not np.all(vector_b == np.zeros(model.vector_size)):
                    similarity = 1 - cosine(vector_a, vector_b)
                    word_scores.append(max(0, similarity))
            if word_scores:
                scores.append(max(word_scores))
        return scores

    scores_1_to_2 = get_scores(vectors1, vectors2)
    scores_2_to_1 = get_scores(vectors2, vectors1)

    combined_scores = scores_1_to_2 + scores_2_to_1

    return mean(combined_scores) if combined_scores else 0


# This function calculates similarity by finding the average vector and finding the cosine similaroty of that. This is what we're using now
def calculate_similarity(vectors1, vectors2, model):
    if vectors1 and vectors2:
        mean_vector1 = mean(array(vectors1), axis=0)
        mean_vector2 = mean(array(vectors2), axis=0)
        uu = np.dot(mean_vector1, mean_vector1)
        vv = np.dot(mean_vector2, mean_vector2)
        if uu == 0 or vv == 0:
            return 0  # or some other appropriate value
        return 1 - cosine(mean_vector1, mean_vector2)
    else:
        return 0

def calculate_similarity3(vectors1, vectors2):
    if vectors1 and vectors2:
        # Remove duplicate vectors by converting to a numpy array and using unique along axis 0
        unique_vectors1 = unique(array(vectors1), axis=0)
        unique_vectors2 = unique(array(vectors2), axis=0)

        # Calculate the mean vectors
        mean_vector1 = mean(unique_vectors1, axis=0)
        mean_vector2 = mean(unique_vectors2, axis=0)

        uu = np.dot(mean_vector1, mean_vector1)
        vv = np.dot(mean_vector2, mean_vector2)
        if uu == 0 or vv == 0:
            return 0  # or some other appropriate value
        return 1 - cosine(mean_vector1, mean_vector2)
    else:
        return 0


def contains_antonyms(words1, words2):
    for word1 in words1:
        if word1 in ANTONYM_PAIRS:
            for antonym in ANTONYM_PAIRS[word1]:
                if antonym in words2:
                    return True
    # check the reverse as well
    for word2 in words2:
        if word2 in ANTONYM_PAIRS:
            for antonym in ANTONYM_PAIRS[word2]:
                if antonym in words1:
                    return True
    return False


def similarity():

    term1 = input("Enter the first medical term: ").lower()
    term2 = input("Enter the second medical term: ").lower()

    # Fetch terms from the database if input is a concept ID
    term1 = get_term(term1)
    term2 = get_term(term2)

    words1 = term1.split()
    words2 = term2.split()

    # Check if terms have the same tag
    print("\n=== Term Analysis ===")
    if term1.split()[-1] == term2.split()[-1]:
        print("Both terms have the same tag.")
    else:
        print("The terms have different tags.")

    # Calculate similarity scores
    vectors1 = get_vectors(term1, loaded_model)
    vectors2 = get_vectors(term2, loaded_model)
    conceptid_1 = databse.get_concept_id(term1)
    conceptid_2 = databse.get_concept_id(term2)
    sim_score1 = calculate_similarity(vectors1, vectors2, loaded_model)
    sim_score2 = avg_of_max_similarity( vectors1, vectors2,loaded_model)
    sim_score3 = calculate_bidirectional_similarity(loaded_model, vectors1, vectors2)
    max_score = max(sim_score1, sim_score2)

    # Display term details and relationships
    print(f"\n=== Details for Term: {term1} (original) ===")
    databse.get_attribute_count(term1)
    parents_1 = databse.get_parents(conceptid_1)
    groups_1 = databse.get_groups_with_attributes(conceptid_1)
    databse.print_parents(parents_1)
    databse.print_groups(groups_1)
    all_relationships_1 = combine_relationships(parents_1, groups_1)
    print(f"Total number of relationships: {len(all_relationships_1)}")

    print(f"\n=== Details for Term: {term2} ===")
    databse.get_attribute_count(term2)
    parents_2 = databse.get_parents(conceptid_2)
    groups_2 = databse.get_groups_with_attributes(conceptid_2)
    databse.print_parents(parents_2)
    databse.print_groups(groups_2)
    all_relationships_2 = combine_relationships(parents_2, groups_2)
    print(f"Total number of relationships: {len(all_relationships_2)}")

    # Display similarity scores
    print("\n=== Similarity Scores ===")
    print(f"Method 1: {sim_score1}")
    print(f"Max Score: {sim_score2}")
    print(f"Min Score: {sim_score3}")
    print(f"Overall Max Similarity Score: {max_score}")

    # Display audit results
    print("\n=== Audit Results ===")
    audit_result = audit_terms(max_score, words1, words2, parents_1, parents_2, groups_1, groups_2, term1, term2)
    print(audit_result)
    print("\n=== End of Analysis ===")

def get_term(input):
    input = input.strip()
    if input.isdigit():
        input = databse.get_term_by_concept_id(input)
        if not input:
            print(f"Error: No active term found for concept ID {input}")
            return
    return input

def get_vectors(term, model):
    words = term.split()
    return [model[word] if word in model else np.zeros(model.vector_size) for word in words]

def combine_relationships(parents, groups):
    """
    Combine parents and groups into a single list of relationships.
    """
    combined_relationships = []

    # Add parents to the combined list
    for parent in parents:
        combined_relationships.append(f"Parent: {parent}")

    # Add groups to the combined list
    for group_id, terms in groups.items():
        for term in terms:
            combined_relationships.append(f"Group {group_id}: {term}")

    return combined_relationships

def check_common_parents(parents_1, parents_2, term1, term2):
    common_parents = set(parents_1).intersection(set(parents_2))
    if len(common_parents) == len(parents_1) == len(parents_2):
        return None  # Both terms have the same parents
    elif len(common_parents) == 1:
        missing_from_term1 = set(parents_2) - common_parents
        missing_from_term2 = set(parents_1) - common_parents
        return f"Justified: Common Parent - {list(common_parents)[0]}. Missing from {term1}: {', '.join(missing_from_term1)}. Missing from {term2}: {', '.join(missing_from_term2)}"
    return None


def check_common_groups(groups_1, groups_2, term1, term2):
    results_term1 = []
    results_term2 = []

    # Combine all relationships from both terms into one list
    combined_relationships_term1 = [relationship for group in groups_1.values() for relationship in group]
    combined_relationships_term2 = [relationship for group in groups_2.values() for relationship in group]

    # Check for missing relationships in both terms
    missing_relationships_term1 = set(combined_relationships_term2) - set(combined_relationships_term1)
    missing_relationships_term2 = set(combined_relationships_term1) - set(combined_relationships_term2)

    # Check for differences in the number of groups
    difference_in_groups = len(groups_2) - len(groups_1)
    if difference_in_groups > 0:
        results_term1.append(f"{abs(difference_in_groups)} groups")
    elif difference_in_groups < 0:
        results_term2.append(f"{abs(difference_in_groups)} groups")

    # Append missing relationships to the results
    if missing_relationships_term1:
        results_term1.extend([rel.split(' -> ')[0] for rel in missing_relationships_term1])
    if missing_relationships_term2:
        results_term2.extend([rel.split(' -> ')[0] for rel in missing_relationships_term2])

    return ", ".join(results_term1) if results_term1 else None, ", ".join(results_term2) if results_term2 else None


def audit_terms(max_score, words1, words2, parents_1, parents_2, groups_1, groups_2, term1, term2):
    if max_score > 0.90000:
        # Check for antonyms
        if contains_antonyms(words1, words2):
            print("Justified: antonyms present")
            return

        # Check for common parents
        parent_check_result = check_common_parents(parents_1, parents_2, term1, term2)
        if parent_check_result:
            print(parent_check_result)
            return

        # Check for common groups and attributes
        group_check_result = check_common_groups(groups_1, groups_2, term1, term2)
        if group_check_result:
            print(group_check_result)
            return
    else:
        print("Justified Difference: Similarity Score below threshold.")

def compute_all_similarity_scores(term, similar_term, model):
    vectors_term = get_vectors(term, model)
    vectors_similar_term = get_vectors(similar_term, model)

    scores = {
        "Max Average": avg_of_max_similarity(model, vectors_term, vectors_similar_term),
        "Two-sided Max Avg": calculate_bidirectional_similarity(model, vectors_term, vectors_similar_term),
        "Average Similarity": calculate_similarity(vectors_term, vectors_similar_term),
        "Unique Average Similarity": calculate_similarity3(vectors_term, vectors_similar_term),
    }

    return scores



import re

def split_term(term):
    # Extract the tag using regex
    tag_match = re.search(r'\(([^)]+)\)$', term)
    if tag_match:
        tag = "(" + tag_match.group(1) + ")"
        # Remove the tag (including the parentheses) from the term to get the words
        words = term[:tag_match.start()].strip().split()
    else:
        tag = None
        words = term.split()

    return words, tag

