import os
import pymysql
import random
import time
import findwords
from modeltrain import modeltrain
from similarity import similarity, split_term
from databse import find_similar_terms_v2, find_terms_with_tag, find_random_terms_with_tag
from findwords import process_selected_integers, process_selected_integersv2, process_selected_terms, process_core


#word2vec_model_path = '/Users/emil07/Desktop/SUMRES/model01.bin'
#if not os.path.isfile(word2vec_model_path):
  #  print("Model file doesn't exist. Training a new model...")
   # modeltrain()
#similarity()
#process_selected_integers()
#print(find_similar_terms_v2("heart (disorder) attack (clinical findings)"))
# Database connection parameters
#print(find_random_terms_with_tag("specimen",50))
#terms_list = ['(disorder)', '(finding)', '(procedure)']
#process_selected_terms(terms_list)
#result_file_path = '/Users/emil07/Desktop/SNDAT/ProcessedTagsv04.txt'
#with open(result_file_path, 'w') as result_file:
 #   result_file.write(str(find_similar_terms_v2("Accidental cephalothin overdose (disorder)")))
    #result_file.write(str(find_similar_terms_v2mod("Accidental cephalothin overdose (disorder)")))

def get_random_cids(filename, num=50):
    with open(filename, 'r') as file:
        lines = file.readlines()[1:]
        cids = [line.split('|')[0] for line in lines]

        if len(cids) < num:
            return cids

        return random.sample(cids, num)


def get_concepts_by_tag(filename, tag, num=100):
    with open(filename, 'r') as file:
        lines = file.readlines()[1:]  # Skip header line
        print(f"Total lines read: {len(lines)}")  # Debugging line
        concepts = [line.strip().split('|') for line in lines]
        filtered_concepts = [concept for concept in concepts if tag_equals(concept[1], tag)]
        print(f"Filtered concepts for tag {tag}: {len(filtered_concepts)}")  # Debugging line
        filtered_concept_ids = [concept[0] for concept in filtered_concepts]  # Assuming the ID is the first element

        if len(filtered_concept_ids) < num:
            return filtered_concept_ids

        sampled_concepts = random.sample(filtered_concept_ids, num)
        print(f"Sampled concept IDs for tag {tag}: {sampled_concepts}")  # Debugging line
        return sampled_concepts


def get_all_concepts_by_tag(filename, tag):
    with open(filename, 'r') as file:
        lines = file.readlines()[1:]  # Skip header line
        print(f"Total lines read: {len(lines)}")  # Debugging line
        concepts = [line.strip().split('|') for line in lines]
        filtered_concepts = [concept for concept in concepts if tag_equals(concept[1], tag)]
        print(f"Filtered all concepts for tag {tag}: {len(filtered_concepts)}")  # Debugging line
        return [concept[0] for concept in filtered_concepts]  # Assuming the ID is the first element


def tag_equals(term, tag):
    main_term, tag01 = split_term(term)
    print(f"Term: {term}, Extracted tag: {tag01}, Expected tag: {tag}")  # Debugging line
    return tag == tag01

def generate_concept_files(tags, file_directory):
    time_log = []

    # Make sure to append the actual filename to the directory path
    file_path = os.path.join(file_directory, 'SNOMEDCORE.txt')

    for tag in tags:
        # Use get_all_concepts_by_tag for 'event' tag or if you need all concepts regardless of the number
        if tag == "event":
            concepts = get_all_concepts_by_tag(file_path, tag)
        else:
            concepts = get_concepts_by_tag(file_path, tag)

        # Construct the output filenames with proper paths
        filename_w = os.path.join(file_directory, f"COREAUDIT04{tag}wCON.txt")
        filename_wi = os.path.join(file_directory, f"COREAUDIT04{tag}woCON.txt")

        start_time = time.time()
        process_core(concepts, 1, filename_w)
        end_time = time.time()
        time_log.append(f"Processing {filename_w}: {end_time - start_time} seconds\n")

        start_time = time.time()
        process_core(concepts, 2, filename_wi)
        end_time = time.time()
        time_log.append(f"Processing {filename_wi}: {end_time - start_time} seconds\n")

        # Write the time log to a file
        with open(os.path.join(file_directory, 'process_time_log03.txt'), 'w') as log_file:
            log_file.writelines(time_log)


# Use the directory path for the file_directory variable
file_directory = "/Users/emil07/Desktop/SUMRES"
tags = ['(procedure)', '(finding)', '(situation)', '(event)']
generate_concept_files(tags, file_directory)


# This is the parameters for the database like the username, password and stuff
db_params = {
    'host': 'localhost',
    'user': 'root',
    'password': 'password',
    'database': 'snomed_ct'
}


EXPECTED_HEADERS = {
    "concept": ["id", "effectiveTime", "active", "moduleId", "definitionStatusId"],
    "description": ["id", "effectiveTime", "active", "moduleId", "conceptId", "languageCode", "typeId", "term", "caseSignificanceId"],
    "relationship": ["id", "effectiveTime", "active", "moduleId", "sourceId", "destinationId", "relationshipGroup", "typeId", "characteristicTypeId", "modifierId"]
}

def validate_file_header(file_path, expected_header):
    with open(file_path, 'r') as f:
        actual_header = f.readline().strip()  # Read the first line
        if actual_header != expected_header:
            raise Exception(f"Header mismatch in {file_path}. Expected: {expected_header}, but found: {actual_header}")


def insert_data_from_file(cursor, table_name, file_path, expected_headers):
    print(f"Starting insertion process for {table_name} table...")

    with open(file_path, "r") as f:
        headers = next(f).strip().split("\t")

        if headers != expected_headers:
            raise Exception(f"Header mismatch in {file_path}. Expected: {expected_headers}, but found: {headers}")

        for idx, line in enumerate(f, start=1):
            values = [val.strip() for val in line.split("\t")]

            if values[2] != '1':  # If the term or concept is not active, skip it
                continue

            if len(values) != len(expected_headers):
                raise Exception(f"Column mismatch in file {file_path} for table {table_name} at line {idx}. "
                                f"Expected {len(expected_headers)} columns, got {len(values)}. Line content: {line}")

            placeholders = ", ".join(["%s"] * len(expected_headers))
            try:
                cursor.execute(f"INSERT INTO {table_name} VALUES ({placeholders})", values)
            except Exception as e:
                raise Exception(
                    f"Error inserting line {line} from file {file_path} into table {table_name}. Error: {e}")

    print(f"Finished adding data to {table_name} table.")


def is_table_empty(cursor, table_name):
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    return count == 0


def populate_database():
    # Establishing the connection
    try:
        conn = pymysql.connect(**db_params)
        cursor = conn.cursor()
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return
    print("Connecting to the database...")

    print("Checking if concept table is empty...")
    # Check if tables are empty
    if not is_table_empty(cursor, "concept"):
        print("The concept table is not empty. Please empty it before proceeding.")
        return
    if not is_table_empty(cursor, "description"):
        print("The description table is not empty. Please empty it before proceeding.")
        return
    if not is_table_empty(cursor, "relationship"):
        print("The relationship table is not empty. Please empty it before proceeding.")
        return

    # If the tables are empty, insert data from files
    try:
        # For the 'conc' table:
        expected_headers_conc = ["id", "effectiveTime", "active", "moduleId", "definitionStatusId"]
        insert_data_from_file(cursor, "concept", "/Users/emil07/Desktop/SUMRES/sct2_Concept_Snapshot_US1000124_20230301.txt", expected_headers_conc)

        # Check if data has been inserted into the 'conc' table
        if is_table_empty(cursor, "concept"):
            print("No data was inserted into the conc table. Exiting without inserting into other tables.")
            return

        # For the 'descds' table:
        expected_headers_descds = ["id", "effectiveTime", "active", "moduleId", "conceptId", "languageCode",
                                   "typeId", "term", "caseSignificanceId"]
        insert_data_from_file(cursor, "description", "/Users/emil07/Desktop/SUMRES/sct2_Description_Snapshot-en_US1000124_20230301.txt", expected_headers_descds)

        # For the 'rels' table:
        expected_headers_rels = ["id", "effectiveTime", "active", "moduleId", "sourceId", "destinationId",
                                 "relationshipGroup", "typeId", "characteristicTypeId", "modifierId"]
        insert_data_from_file(cursor, "relationship", "/Users/emil07/Desktop/SUMRES/sct2_Relationship_Snapshot_US1000124_20230301.txt", expected_headers_rels)

        # Committing the changes
        conn.commit()

    except Exception as e:
        print(f"Error processing files: {e}")
    finally:
        cursor.close()
        conn.close()


#populate_database()