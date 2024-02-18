import pymysql
import random
import similarity

IS_A_TYPE_ID = 116680003
FULLY_SPECIFIED_NAME_TYPE_ID = 900000000000003001

db_params = {
    'host': 'localhost',
    'user': 'root',
    'password': 'password',
    'database': 'snomed_ct'
}

def get_term_by_concept_id(concept_id):
    with pymysql.connect(**db_params) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT term FROM description WHERE conceptId = %s AND active = 1 AND typeId = %s", (concept_id,FULLY_SPECIFIED_NAME_TYPE_ID))
        result = cursor.fetchone()
        return result[0] if result else None
def get_concept_id(term):
    with pymysql.connect(**db_params) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT description.conceptId FROM description, concept WHERE description.term = %s AND description.conceptId = concept.id", (term,))
        result = cursor.fetchone()
        return result[0] if result else None

def get_attribute_count(term):
    concept_id = get_concept_id(term)
    if not concept_id:
        print(f"No concept found for term: {term}")
        return 0

    print_fully_specified_name(concept_id)
    #print_all_relationships(concept_id)

    with pymysql.connect(**db_params) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM rels WHERE sourceId = %s AND typeId != %s", (concept_id, FULLY_SPECIFIED_NAME_TYPE_ID))
        attribute_count = cursor.fetchone()[0]

def print_fully_specified_name(concept_id):
    with pymysql.connect(**db_params) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT descds.term FROM description AS descds, concept AS conc WHERE descds.conceptId = %s AND descds.conceptId = conc.id AND descds.typeId = %s AND conc.active = 1 AND descds.active =1", (concept_id, FULLY_SPECIFIED_NAME_TYPE_ID))
        fsn = cursor.fetchone()
        if fsn:
            print(f"Fully Specified Name: {fsn[0]}")

def get_fully_specified_name(concept_id):
    #print("Running FSN gathering\n")
    with pymysql.connect(**db_params) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT descds.term FROM description AS descds, concept AS conc WHERE descds.conceptId = %s AND descds.typeId = %s AND descds.conceptId = conc.id AND descds.active = 1 AND conc.active = 1", (concept_id, FULLY_SPECIFIED_NAME_TYPE_ID))
        fsn = cursor.fetchone()
        return fsn[0] if fsn else None

def get_parents(concept_id):
    parents_list = []
    #print("Running parent gathering\n")
    with pymysql.connect(**db_params) as conn:
        cursor = conn.cursor()

        # Fetch destinationIds for the given concept_id and IS_A_TYPE_ID
        cursor.execute("SELECT DISTINCT destinationId FROM relationship  WHERE sourceId = %s AND typeId = %s AND active = 1",
                       (concept_id, IS_A_TYPE_ID))
        destination_ids = [row[0] for row in cursor.fetchall()]

        if not destination_ids:  # Check if destination_ids is empty
            return parents_list

        # Fetch terms for these destinationIds
        query = "SELECT DISTINCT term, conceptId FROM description WHERE conceptId IN (" + ','.join(
            ['%s'] * len(destination_ids)) + ") AND active = 1"
        cursor.execute(query, tuple(destination_ids))
        parents = {row[1]: row[0] for row in cursor.fetchall()}

        # Filter out terms that are also children of another term in the list
        to_remove = set()
        for dest_id in destination_ids:
            cursor.execute(
                "SELECT DISTINCT sourceId FROM relationship WHERE destinationId = %s AND typeId = %s AND active = 1",
                (dest_id, IS_A_TYPE_ID))
            children = {row[0] for row in cursor.fetchall()}
            to_remove.update(children.intersection(destination_ids))

        for rem_id in to_remove:
            if rem_id in parents:
                del parents[rem_id]

        parents_list = list(parents.values())

    return parents_list


def print_parents(input_data):
    if isinstance(input_data, int):  # If input_data is a concept_id
        parents = get_parents(input_data)
    elif isinstance(input_data, list):  # If input_data is a list of parent terms
        parents = input_data
    else:
        print("Invalid input!")
        return

    print("Parents:", parents)



def print_all_relationships(concept_id):
    with pymysql.connect(**db_params) as conn:
        cursor = conn.cursor()

        # Fetch attribute relationships (excluding IS_A_TYPE_ID)
        cursor.execute("SELECT DISTINCT typeId, destinationId FROM rels WHERE sourceId = %s AND typeId != %s AND active = 1",
                       (concept_id, IS_A_TYPE_ID))
        attribute_rels = cursor.fetchall()

        # Fetch terms for these destinationIds
        destination_ids = [row[1] for row in attribute_rels]
        cursor.execute("SELECT DISTINCT term, conceptId FROM descds WHERE conceptId IN (%s) AND active = 1" % ','.join(
            ['%s'] * len(destination_ids)), tuple(destination_ids))
        terms = {row[1]: row[0] for row in cursor.fetchall()}

        all_relationships = []
        for rel in attribute_rels:
            rel_type = rel[0]
            dest_id = rel[1]
            all_relationships.append(f"{rel_type} -> {terms[dest_id]}")

        print("All Relationships:", all_relationships)



def get_term_for_concept_id(concept_id):
    #print("Running getting term for conceptid gathering\n")
    fsn = get_fully_specified_name(concept_id)
    if fsn:
        return fsn
    else:
        with pymysql.connect(**db_params) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT term FROM description WHERE conceptId = %s LIMIT 1 AND typeId = %s", (concept_id,IS_A_TYPE_ID))
            result = cursor.fetchone()
            return result[0] if result else None


def get_groups_with_attributes(concept_id):
    groups = {}
    with pymysql.connect(**db_params) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT relationshipGroup, typeId, destinationId FROM relationship WHERE sourceId = %s AND typeId != %s AND active = 1 ORDER BY relationshipGroup",
            (concept_id, IS_A_TYPE_ID))

        for group_id, type_id, dest_id in cursor.fetchall():
            attribute_name = get_term_for_concept_id(type_id)
            target_value = get_term_for_concept_id(dest_id)

            if group_id not in groups:
                groups[group_id] = []
            groups[group_id].append(f"{attribute_name} -> {target_value}")

    return groups

def print_groups(groups):
    for group_id, terms in groups.items():
        print(f"Group {group_id}:", terms)


def find_similar_terms_v2(term):
    #print("Initial Meathod\n\n")
    # Split the term into words and tag
    words, tag = similarity.split_term(term)
    # *words, tag = term.split()
    print("Words: ",words)
    print("Tag: ",tag)

    similar_terms = {}  # Now a dictionary to store conceptId: term pairs

    with pymysql.connect(**db_params) as conn:
        cursor = conn.cursor()

        # For each word in the term, query the database for terms that contain the word and the tag
        for word in words:
            query = """
            SELECT descds.term, descds.conceptId 
            FROM description AS descds 
            JOIN concept AS conc ON descds.conceptId = conc.id 
            WHERE descds.term LIKE %s 
            AND descds.term LIKE %s 
            AND descds.active = 1 
            AND conc.active = 1
            AND descds.typeId = %s
            """
            cursor.execute(query, ('%' + word + '%', '%' + tag, FULLY_SPECIFIED_NAME_TYPE_ID))
            results = cursor.fetchall()

            for result in results:
                fetched_term, concept_id = result
                if concept_id and concept_id not in similar_terms:  # Ensure concept_id is not None and is unique
                    similar_terms[concept_id] = fetched_term  # Add term to the dictionary with concept_id as the key

    return similar_terms



def find_terms_with_tag(tag):
    pairs = {}

    with pymysql.connect(**db_params) as conn:
        cursor = conn.cursor()

        # For each word in the term, query the database for terms that contain the word and the tag
        query = """SELECT descds.term, descds.conceptId 
                   FROM description AS descds 
                   JOIN concept AS conc ON descds.conceptId = conc.id 
                   WHERE descds.term LIKE %s 
                   AND descds.active = 1 
                   AND conc.active = 1 
                   AND descds.typeId = %s"""

        cursor.execute(query, ('%' + tag, FULLY_SPECIFIED_NAME_TYPE_ID))
        results = cursor.fetchall()

        for result in results:
            fetched_term, concept_id = result
            pairs[concept_id] = fetched_term

    return pairs

import random

def find_random_terms_with_tag(tag, n):
    terms = find_terms_with_tag(tag)
    if len(terms) < n:
        print(f"Warning: Only {len(terms)} concepts available for tag '{tag}'. Returning all available concepts.")
        return terms

    sampled_keys = random.sample(list(terms.keys()), n)
    return {key: terms[key] for key in sampled_keys}


def tag_equals(concept_parts, tag):
    # concept_parts is a list where the first element is expected to be the concept ID or term
    concept = concept_parts[0]

    if concept.isdigit():
        term = get_fully_specified_name(concept)
    else:
        term = concept

    words, tag01 = similarity.split_term(term)

    return tag == tag01
