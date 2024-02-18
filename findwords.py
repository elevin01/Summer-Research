import pandas as pd
from gensim.models import KeyedVectors
from collections import Counter, defaultdict
import re
import databse
import similarity

from databse import get_parents, get_groups_with_attributes, get_concept_id
from similarity import check_common_parents, check_common_groups, get_term, split_term


# Load the model here
# https://bio.nlplab.org/#word-vector-tools this is where I got the model from
new_model_path = '/Users/emil07/Desktop/SNDAT/wikipedia-pubmed.model'
loaded_model = KeyedVectors.load(new_model_path)

# Gets the parents and attributes included in each group of a term.
def get_term_details(concept_id, term):
    print(f"Getting details for term: {term}, concept_id: {concept_id}")  # Printing in the consle to keep track of it

    if concept_id is None:  # Check if concept_id is None
        print(f"Warning: concept_id is None for term: {term}. Skipping.")
        return None  # Return None or an appropriate default value

    parents = get_parents(concept_id)
    groups_with_attributes = get_groups_with_attributes(concept_id)
    return {
        'Parents': parents,
        'Groups': groups_with_attributes
    }

# def audit_terms(term1_details, similar_term_details, term1, similar_term, similarity_score):
#     concept_id_term1 = get_concept_id(term1)
#     concept_id_similar_term = get_concept_id(similar_term)
#
#     parents_1 = set(term1_details['Parents'])
#     parents_2 = set(similar_term_details['Parents'])
#     groups_1 = term1_details['Groups']
#     groups_2 = similar_term_details['Groups']
#
#     missing_parents_term1 = parents_2 - parents_1
#     missing_parents_similar_term = parents_1 - parents_2
#
#     # Use the check_common_groups function to handle the comparison of groups and attributes
#     common_groups_result_term1, common_groups_result_term2 = check_common_groups(groups_1, groups_2, term1, similar_term)
#
#     result = ""
#
#     # Process term1
#     result += f"{concept_id_term1} {term1} missing:"
#     if missing_parents_term1:
#         result += f" Parents: {', '.join(missing_parents_term1)},"
#     else:
#         result += " Parents: ,"
#     if common_groups_result_term1:
#         result += f" Groups: {common_groups_result_term1}"
#     else:
#         result += " Groups:"
#     result += "\n"
#
#     # Process similar_term
#     result += f"{concept_id_similar_term} {similar_term} missing:"
#     if missing_parents_similar_term:
#         result += f" Parents: {', '.join(missing_parents_similar_term)},"
#     else:
#         result += " Parents: ,"
#     if common_groups_result_term2:
#         result += f" Groups: {common_groups_result_term2}"
#     else:
#         result += " Groups:"
#     result += "\n"
#
#     result += f"similarity score: {similarity_score}\n"
#     return result

def audit_terms2(concept_id_term1, concept_id_similar_term, term1_details, similar_term_details, term1, similar_term, similarity_score):
    # Check if the provided details have the expected keys
    if not all(key in term1_details for key in ['Parents', 'Groups']):
        print(f"Error: Missing keys in details for term: {term1}")
        return None

    if not all(key in similar_term_details for key in ['Parents', 'Groups']):
        print(f"Error: Missing keys in details for similar term: {similar_term}")
        return None

    common_p_count = common_parents_count(term1_details,similar_term_details)
    siblings = False
    if common_p_count == len(similar_term_details['Parents']) and common_p_count == len(term1_details['Parents']) and len(similar_term_details['Parents']) == len(similar_term_details['Parents']):
        siblings = True
    # Use the check_common_attributes function to get the missing attributes from term1
    missing_attributes = check_common_attributes_v3(term1_details, similar_term_details)
    # Condition that excludes all concepts that are not sibilings
    if not siblings:
            return None
    # Construct the result string
    result = f"{concept_id_similar_term}\t{similar_term}\t{similarity_score}\t"
    result += f"{len(similar_term_details['Parents'])}\t"
    result += f"{sum([len(group) for group in similar_term_details['Groups'].values()])}\t"  # This gives the total number of attributes
    result += f"{len(similar_term_details['Groups'])}\t"
    result += f"{common_p_count}\t"
    result += f"{siblings}\t"
    result += ', '.join(missing_attributes) if missing_attributes else "None"
    return result


def process_selected_terms(terms, n=50):
    # Path to the resultRS.txt file
    result_file_path = '/Users/emil07/Desktop/SNDAT/ProcessedTags_ch02.txt'

    # Open the file for writing
    with open(result_file_path, 'w') as result_file:
        for term in terms:
            concept_id_term_dict = databse.find_random_terms_with_tag(term, n)
            count_originals_with_similars = 0
            for concept_id, actual_term in concept_id_term_dict.items():
                print(f"Processing concept_id: {concept_id} for term: {actual_term} \n")
                if actual_term:
                    # Get the details for the original term
                    original_term_details = get_term_details(concept_id,actual_term)

                    # Write term1 details to the file
                    term1_line = f"\n{concept_id}\t{actual_term}\t\t{len(original_term_details['Parents'])}\t{sum([len(group) for group in original_term_details['Groups'].values()])}\t{len(original_term_details['Groups'])}\t\t\t\t\n"
                    result_file.write(term1_line)

                    # Find similar words for the term
                    similar_terms = databse.find_similar_terms_v2(actual_term)
                    filtered_terms = filter_terms(actual_term, similar_terms, loaded_model)
                    filtered_terms = filter_terms_by_constraints(actual_term, filtered_terms)
                    if filtered_terms:
                        count_originals_with_similars += 1

                    # Loop through the filtered terms and print their details
                    for similar_term_id, similar_term in filtered_terms.items():
                        similar_term_details = get_term_details(similar_term_id, similar_term)
                        if similar_term_details:
                            audit_result = audit_terms2(concept_id, similar_term_id, original_term_details,
                                                        similar_term_details, actual_term, similar_term,
                                                        similarity.calculate_similarity(
                                                            similarity.get_vectors(actual_term, loaded_model),
                                                            similarity.get_vectors(similar_term, loaded_model),
                                                            loaded_model))
                            if check_attribute_count(original_term_details, similar_term_details, actual_term):
                                print(audit_result, "\n")
                                result_file.write(str(audit_result) + '\n')
                        else:
                            print(f"Warning: No details found for similar term {similar_term}. Skipping.")
                else:
                    print(f"Warning: No term found for concept_id {concept_id}")

            print(f"{count_originals_with_similars} original terms have at least one similar term for {term}.")
            result_file.write(
                f"\n\n{count_originals_with_similars} original terms have at least one similar term for {term}.\n\n")

    print("Processing complete. Results written to file.")

def process_core(cids, tcon, filepath):
    result_file_path = filepath
    same_attr_count = 0

    with open(result_file_path, 'w') as result_file:
        for cid in cids:
            concept_id = cid
            actual_term = databse.get_fully_specified_name(cid)
            count_originals_with_similars = 0
            print(f"Processing concept_id: {concept_id} for term: {actual_term} \n")
            if actual_term:
                # Get the details for the original term
                original_term_details = get_term_details(concept_id, actual_term)

                # Write term1 details to the file
                term1_line = f"\n{concept_id}\t{actual_term}\t\t{len(original_term_details['Parents'])}\t{sum([len(group) for group in original_term_details['Groups'].values()])}\t{len(original_term_details['Groups'])}\t\t\t\t\n"
                result_file.write(term1_line)

                # Find similar words for the term
                similar_terms = databse.find_similar_terms_v2(actual_term)
                filtered_terms = filter_terms_beta(actual_term, similar_terms, loaded_model)
                if tcon == 1:
                    filtered_terms = filter_terms_by_constraints(actual_term, filtered_terms)
                if filtered_terms:
                    count_originals_with_similars += 1

                # Loop through the filtered terms and print their details
                for similar_term_id, similar_term in filtered_terms.items():
                    similar_term_details = get_term_details(similar_term_id, similar_term)
                    if similar_term_details:
                        audit_result = audit_terms2(concept_id, similar_term_id, original_term_details,
                                                    similar_term_details, actual_term, similar_term,
                                                    similarity.calculate_similarity(
                                                        similarity.get_vectors(actual_term, loaded_model),
                                                        similarity.get_vectors(similar_term, loaded_model),
                                                        loaded_model))
                        if check_attribute_count(original_term_details, similar_term_details, actual_term):
                            print(audit_result, "\n")
                            if audit_result:
                                result_file.write(str(audit_result) + '\n')
                                if sum([len(group) for group in similar_term_details['Groups'].values()]) == sum([len(group) for group in original_term_details['Groups'].values()]):
                                    same_attr_count +=1
                    else:
                        print(f"Warning: No details found for similar term {similar_term}. Skipping.")
            else:
                print(f"Warning: No term found for concept_id {concept_id}")

        #print(f"{count_originals_with_similars} original terms have at least one similar term for {actual_term}.")
        #result_file.write(
         #   f"\n\n{count_originals_with_similars} original terms have at least one similar term for {actual_term}.\n\n")
        result_file.write(f"\n Total Concepts with same number of attributes : {same_attr_count} \n\n")

    print("Processing complete. Results written to file.")





def process_selected_integers():
    # Path to the selected_integers.txt file
    selected_integers_path = '/Users/emil07/Desktop/SNDAT/selected_integers.txt'
    # Path to the resultRS.txt file
    result_file_path = '/Users/emil07/Desktop/SNDAT/resultRSAV_v01.txt'

    # Read the selected_integers.txt file
    with open(selected_integers_path, 'r') as file:
        concept_ids = file.readlines()

    # Open the resultRS.txt file for writing
    with open(result_file_path, 'w') as result_file:
        for concept_id in concept_ids:
            concept_id = concept_id.strip()
            if concept_id.isdigit():
                print(f"Processing concept_id: {concept_id} \n")
                # Get the term for the concept ID
                term = databse.get_fully_specified_name(concept_id)
                if term:
                    # Get the details for the original term
                    original_term_details = get_term_details(term)

                    # Write term1 details to the file
                    term1_line = f"\n{get_concept_id(term)}\t{term}\t\t{len(original_term_details['Parents'])}\t{sum([len(group) for group in original_term_details['Groups'].values()])}\t{len(original_term_details['Groups'])}\t\t\t\t\n"
                    result_file.write(term1_line)

                    # Find similar words for the term
                    similar_words = databse.find_similar_terms_v2(term)
                    filtered_terms = filter_terms(term, similar_words, loaded_model)
                    filtered_terms = filter_terms_by_constraints(term, filtered_terms)
                    filtered_details = []

                    # Loop through the filtered terms and print their details
                    for filtered_term in filtered_terms:
                        similar_term_id = get_concept_id(filtered_term)
                        similar_term = databse.get_fully_specified_name(similar_term_id)
                        similar_term_details = get_term_details(similar_term)
                        if similar_term_details:
                            filtered_details.append(similar_term_details)
                        if similar_term_details is not None:  # Check if get_term_details returned None
                            audit_result = audit_terms2(concept_id, similar_term_id, original_term_details, similar_term_details, term, similar_term,
                                                       similarity.calculate_similarity(
                                                           similarity.get_vectors(term, loaded_model),
                                                           similarity.get_vectors(similar_term, loaded_model),loaded_model))
                            print(audit_result, "\n")
                            result_file.write(str(audit_result) + '\n')
                        else:
                            print(f"Warning: No details found for similar term {similar_term}. Skipping.")
                else:
                    print(f"Warning: No term found for concept_id {concept_id}")
            else:
                print(f"Warning: Invalid concept_id: {concept_id}. Skipping.")

    print("Processing complete. Results written to resultRSAV.txt.")


# This
def filter_terms(term, similar_terms, model):
    # Convert the input term into vectors
    vectors1 = similarity.get_vectors(term, loaded_model)

    # Dictionary to store terms with similarity above 0.9
    filtered_terms = {}

    for concept_id, similar_term in similar_terms.items():
        # Convert the similar term into vectors
        vectors2 = similarity.get_vectors(similar_term, loaded_model)
        # Calculate the cosine similarity between the vectors
        similarity_score = similarity.calculate_similarity(vectors1, vectors2, loaded_model)

        if similarity_score >= 0.9:
            if concept_id != get_concept_id(term):
                filtered_terms[concept_id] = similar_term
    return filtered_terms

def filter_terms_beta(term, similar_terms, model):
    # Convert the input term into vectors
    vectors1 = similarity.get_vectors(term, loaded_model)

    # Dictionary to store terms with similarity above 0.9
    filtered_terms = {}
    print(f"Going to go through about {len(similar_terms)} now")
    for concept_id, similar_term in similar_terms.items():
        # Convert the similar term into vectors
        vectors2 = similarity.get_vectors(similar_term, loaded_model)
        # Calculate the cosine similarity between the vectors
        print(f"\nSimilarity being checked now: {similar_term} vs  {concept_id}")
        similarity_score = similarity.calculate_similarity(vectors1, vectors2, loaded_model)

        if similarity_score >= 0.0:
            if concept_id != get_concept_id(term):
                filtered_terms[concept_id] = similar_term
                print(f"Adding term to filtered term {similar_term} with a score of {similarity_score}")
    return filtered_terms

def get_majority_details(filtered_details, threshold_ratio=0.5):
    # Counters to keep track of parents and attributes
    parents_counter = Counter()
    attributes_counter = Counter()

    # Dictionary to keep track of groups and their attributes
    groups_dict = defaultdict(list)

    # Iterate through the filtered details to count occurrences
    for details in filtered_details:
        if details is not None:
            parents_counter.update(details['Parents'])
            for group, attributes in details['Groups'].items():
                groups_dict[group].extend(attributes)
                attributes_counter.update(attributes)

    # Determine the majority based on the threshold ratio
    majority_parents = [parent for parent, count in parents_counter.items() if count / len(filtered_details) >= threshold_ratio]
    majority_attributes = [attribute for attribute, count in attributes_counter.items() if count / len(filtered_details) >= threshold_ratio]

    # Determine the majority groups
    majority_groups = {group: Counter(attributes) for group, attributes in groups_dict.items()}
    for group, attributes in majority_groups.items():
        majority_groups[group] = [attribute for attribute, count in attributes.items() if count / len(filtered_details) >= threshold_ratio]

    return {
        'Parents': majority_parents,
        'Attributes': majority_attributes,
        'Groups': majority_groups
    }


def audit_majority_details(concept_id_term, original_term_details, majority_details, term):
    # Check if the provided details have the expected keys
    if not all(key in original_term_details for key in ['Parents', 'Groups']):
        print(f"Error: Missing keys in details for term: {term}")
        return None

    if not all(key in majority_details for key in ['Parents', 'Groups']):
        print(f"Error: Missing keys in majority details for term: {term}")
        return None

    groups_1 = original_term_details['Groups']
    groups_2 = majority_details['Groups']

    # Use the check_common_groups function to handle the comparison of groups and attributes
    common_groups_result_term1, _ = check_common_groups(groups_1, groups_2, term, term)

    # Initialize result string
    result = f"{concept_id_term}\t{term}\t"
    result += f"{len(original_term_details['Parents'])}\t"
    result += f"{sum([len(group) for group in original_term_details['Groups'].values()])}\t"
    result += f"{len(original_term_details['Groups'])}\t"
    if common_groups_result_term1:
        result += f"{common_groups_result_term1}"
    else:
        result += "None"

    result = f"{result}\n"

    return result


def filter_terms_by_constraints(term, filtered_similar_terms):
    # Split the main term into words and tag
    term_words, term_tag = split_term(term)

    # Dictionary to store terms that pass the constraints
    valid_similar_terms = {}

    for concept_id, similar_term in filtered_similar_terms.items():
        # Split the similar term into words and tag
        similar_term_words, similar_term_tag = split_term(similar_term)

        # If the tags are not the same, skip the current iteration
        if term_tag != similar_term_tag:
            continue

        # Check if the lengths are the same
        if len(term_words) != len(similar_term_words):
            continue

        # Find the differing words and their indices
        differing_words = [(i, a, b) for i, (a, b) in enumerate(zip(term_words, similar_term_words)) if a != b]

        # If there's only one differing word and it's in the same position for both terms, add to valid dictionary
        if len(differing_words) == 1:
            valid_similar_terms[concept_id] = similar_term

    return valid_similar_terms


def adjust_target_values(term, missing_attributes):
    """
    Adjust the target values of missing attributes based on the unique words in the term.

    Parameters:
    - term (str): The term whose missing attributes are being adjusted.
    - missing_attributes (str): The string of missing attributes and their target values.

    Returns:
    - str: The adjusted missing attributes string.
    """
    # Split the term into words
    term_words = set(term.split())

    # Split the missing attributes string into lines
    lines = missing_attributes.split(', ')

    # Process each line
    for i, line in enumerate(lines):
        # Check if the line contains the ' -> ' delimiter
        if ' -> ' in line:
            # Split the line into attribute and target value
            attribute, target_value = line.split(' -> ')

            # Find the unique words in the target value
            target_value_words = set(target_value.split())

            # Find the words that are unique to the target value (not present in the term)
            unique_words = target_value_words - term_words

            # Replace the unique words in the target value with the unique words from the term
            for word in unique_words:
                for term_word in term_words:
                    if term_word not in target_value_words:
                        target_value = target_value.replace(word, term_word)
                        break

            # Update the line with the adjusted target value
            lines[i] = f"{attribute} -> {target_value}"
        elif "groups" in line:
            # Add the word "Missing" before the number of groups
            lines[i] = f"Groups -> Missing {line}"

    # Join the lines back into a string and return
    return ", ".join(lines)

def check_common_attributes(term1_details, similar_term_details):

    # Combine all attributes from both terms into two separate lists
    attributes_term1 = [attribute.split(' -> ')[0] for group in term1_details['Groups'].values() for attribute in group]
    attributes_similar_term = [attribute.split(' -> ')[0] for group in similar_term_details['Groups'].values() for attribute in group]

    # Compare the two lists to find out which attributes are missing in each term
    missing_attributes_term1 = set(attributes_similar_term) - set(attributes_term1)
    missing_attributes_similar_term = set(attributes_term1) - set(attributes_similar_term)

    # Return a list containing all attributes that are present in the similar term but are missing in term1
    return list(missing_attributes_term1)


def split_attribute(attribute):
    parts = attribute.split(' -> ')
    return (parts[0], parts[1]) if len(parts) > 1 else (parts[0], None)


def list_difference(a, b):
    b_names = [split_attribute(item)[0] for item in b.copy()]  # creating a copy

    # Compare only attribute name at position 0 (split attribute into name and target using function) but when returning, return the whole thing
    return [item for item in a if split_attribute(item)[0] not in b_names or b_names.remove(split_attribute(item)[0])]


def check_common_attributes_v2(term1_details, similar_term_details):
    # Combine all attributes from both terms into two separate lists
    attributes_term1 = [attribute for group in term1_details['Groups'].values() for attribute in group]
    attributes_similar_term = [attribute for group in similar_term_details['Groups'].values() for attribute in group]

    # Find the difference between two lists
    missing_attributes_term1 = list_difference(attributes_similar_term, attributes_term1)
    missing_attributes_similar_term = list_difference(attributes_term1, attributes_similar_term)

    # Return a list containing all attributes that are present in the similar term but are missing in term1
    return missing_attributes_term1


def common_parents_count(term_details_1, term_details_2):
    # Extract parents from the term details assuming that there will be no duplicates
    parents_1 = set(term_details_1['Parents'])
    parents_2 = set(term_details_2['Parents'])

    # Find the intersection of the two sets of parents
    common_parents = parents_1.intersection(parents_2)

    return len(common_parents)


def check_common_attributes_v3(term1_details, term2_details):
    attributes_term1 = [(attribute.split(' -> ')[0], attribute) for group in term1_details['Groups'].values() for
                        attribute in group]
    attributes_term2 = [(attribute.split(' -> ')[0], attribute) for group in term2_details['Groups'].values() for
                        attribute in group]

    missing_attributes = list_difference_v2(attributes_term1, attributes_term2)

    # Print the lists and the result for debugging
    print(f"Attributes for term1: {attributes_term1}")
    print(f"Attributes for term2: {attributes_term2}")
    print(f"Missing attributes: {missing_attributes}")

    return  missing_attributes


def list_difference_v2(a, b):
    unique_attr_names = set([attr[0] for attr in b])

    missing = []

    for attr_name in unique_attr_names:
        count_in_a = sum(1 for attr in a if attr[0] == attr_name)
        count_in_b = sum(1 for attr in b if attr[0] == attr_name)

        if count_in_b > count_in_a:
            missing.extend([attr[1] for attr in b if attr[0] == attr_name][count_in_a:])

    return missing


def process_selected_integersv2():
    selected_integers_path = '/Users/emil07/Desktop/SNDAT/selected_integers.txt'
    result_file_path = '/Users/emil07/Desktop/SNDAT/resultRSsmoothop.txt'

    with open(selected_integers_path, 'r') as file:
        concept_ids = file.readlines()

    with open(result_file_path, 'w') as result_file:
        # Write column headers
        headers = "conceptID\tterm\t" + "\t".join(["Max Average", "Two-sided Max Avg", "Average Similarity", "Unique Average Similarity", "Min Average"]) + "\n"
        result_file.write(headers)

        for concept_id in concept_ids:
            concept_id = concept_id.strip()
            if concept_id.isdigit():
                print(f"Processing concept_id: {concept_id} \n")
                term = databse.get_fully_specified_name(concept_id)
                if term:
                    # Write term details to the file
                    term_details_line = f"{concept_id}\t{term}\n\n"
                    result_file.write(term_details_line)

                    similar_words = databse.find_similar_terms_v2(term)
                    similar_terms = filter_terms_by_constraints(term, similar_words)
                    for similar_term in similar_terms:
                        similar_term_id = get_concept_id(similar_term)
                        similar_term_name = databse.get_fully_specified_name(similar_term_id)
                        if similar_term_name:
                            scores = similarity.compute_all_similarity_scores(term, similar_term_name, loaded_model)
                            scores_line = f"{similar_term_id}\t{similar_term_name}\t" + "\t".join([str(scores[key]) for key in scores]) + "\n"
                            print(scores_line)
                            result_file.write(scores_line)
                        else:
                            print(f"Warning: No details found for similar term {similar_term}. Skipping.")
                else:
                    print(f"Warning: No term found for concept_id {concept_id}")
            else:
                print(f"Warning: Invalid concept_id: {concept_id}. Skipping.")

    print("Processing complete. Results written to resultRSsmooth.txt.")


def check_attribute_count(term_details, similar_term_details, result):
    last_term = result.split()[-1]

    if sum([len(group) for group in similar_term_details['Groups'].values()]) != sum(
            [len(group) for group in term_details['Groups'].values()]):
        return True
    elif last_term != "None":
        return True
    else:
        return False

