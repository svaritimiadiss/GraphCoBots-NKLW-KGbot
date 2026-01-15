from rasa_sdk import Tracker, Action
from rasa_sdk.executor import CollectingDispatcher
from typing import Dict, Text, Any, List
from rasa_sdk.events import SlotSet, ReminderScheduled, AllSlotsReset
from neo4j import GraphDatabase
import datetime
import random
from thefuzz import process  # Import the necessary module from thefuzz
import re
import requests
from actions import utils
import yaml
import os
from dotenv import load_dotenv, set_key


# Load the responses from the JSON file just ONCE
with open('actions/genai_placeholders.yml', 'r', encoding='utf-8') as f:
    genai_data = yaml.safe_load(f)

load_dotenv()

#* Generative service endpoints
GENAI_BASE_URL = os.getenv("FASTAPI_APP_URL")
OPENAI_RESPONSE_ENDPOINT = os.getenv("OPENAI_RESPONSE_ENDPOINT")

#* Vector Store parameters
VECTOR_DB_NAME = genai_data["vector_stores"]["vector_db"]
COLLECTION_NAME = genai_data["vector_stores"]["collection"]

#* Generative models
CHAT_MODEL = genai_data["models"]["chat"]

# def print_friends(tx, name):
#     names = []
#     for record in tx.run("MATCH (a:WRITER)-[:MARRIEDTO]->(friend:WRITER) WHERE a.name = $name "
#                          "RETURN friend.name ORDER BY friend.name", name=name):
#         print("record friend.name: {}".format(record["friend.name"]))
#         print("record: {}".format(record))
#         names.append(record["friend.name"])
#         print("names: ", names)
#
#         # return record["friend.name"]
#
#     return record["friend.name"]


def print_books_type(tx, book_type_pl):
    # print("book_type_pl: ", book_type_pl)

    books_names_list = []
    for record in tx.run(
            "MATCH(a: WRITER)-[: WROTE]->(book) WHERE a.name = 'Νίκος Καζαντζάκης' AND book.type_pl = $book_type_pl "
            "RETURN book.name", book_type_pl=book_type_pl):
        # print("record book.name: {}".format(record["book.name"]))
        # print("record: {}".format(record))
        books_names_list.append(record["book.name"])
        # print("book_type_list: ", books_names_list)

        # return record["book.name"]

    count_book_type_list = len(books_names_list)
    # print("count_book_type_list: ", count_book_type_list)
    # return record["book.name"]
    return count_book_type_list, books_names_list


def print_location_countries(tx, relation):
    location_countries_list = []
    for record in tx.run(
            f"MATCH (a:WRITER)-[: {relation}]->(location) WHERE a.name='Νίκος Καζαντζάκης' "
            "RETURN location.country"):
        location_countries_list.append(record["location.country"])

        # return record["book.name"]

    # count_book_type_list = len(location_name_list)
    # print("count_book_type_list: ", count_book_type_list)
    # return record["book.name"]

    location_countries_list = list(set(location_countries_list))
    # print(location_countries_list)

    return location_countries_list


def print_location_areas(tx, relation, location_areas):
    # print("location_areas: ", location_areas)

    location_areas_list = []
    for record in tx.run(
            "MATCH (a:WRITER)-[:TRAVELEDTO]->(location) WHERE a.name='Νίκος Καζαντζάκης' AND location.type = location_areas "
            "RETURN location.name", relation=relation, location_areas=location_areas):
        # print("record location.name: {}".format(record["location.name"]))
        # print("record: {}".format(record))
        location_areas_list.append(record["location.name"])
        # print("location_name_list: ", location_areas_list)

        # return record["book.name"]

    # count_book_type_list = len(location_name_list)
    # print("count_book_type_list: ", count_book_type_list)
    # return record["book.name"]

    location_areas_list = list(set(location_areas_list))

    return location_areas_list


def print_friends_type(tx, friends_type):
    # print("book_type_pl: ", book_type_pl)

    friends_names_list = []
    for record in tx.run(
            "MATCH (k:WRITER {name_en: 'Nikos Kazantzakis'})-[:RELATEDTO]->(f) WHERE f.type = 'φίλος' "
            "RETURN f.name", friends_type=friends_type):
        # print("record book.name: {}".format(record["book.name"]))
        # print("record: {}".format(record))
        friends_names_list.append(record["f.name"])
        # print("book_type_list: ", books_names_list)

        # return record["book.name"]

    # print("count_book_type_list: ", count_book_type_list)
    # return record["book.name"]
    return friends_names_list


def print_relatives_type(tx, relatives_type):
    # print("book_type_pl: ", book_type_pl)

    relatives_type_list = []
    for record in tx.run(
            "MATCH (r:RELATIVE)"
            "RETURN r.name", relatives_type=relatives_type):
        # print("record book.name: {}".format(record["book.name"]))
        # print("record: {}".format(record))
        relatives_type_list.append(record["r.name"])
        # print("book_type_list: ", books_names_list)

        # return record["book.name"]

    return relatives_type_list


def print_publicationyear(tx, publicationyear):
    publicationyear_list = []

    publicationyear = int(publicationyear)
    # print("publicationyear int: ", publicationyear)

    # Το επιστρέφει ως text αλλά για το query χρειάζεται να είναι int!!!
    # print("type publicationyear: ", type(publicationyear))

    for record in tx.run(
            "MATCH (k:WRITER {name_en: 'Nikos Kazantzakis'})-[:WROTE]->(b) "
            "WHERE b.PublicationYear = $publicationyear "
            "RETURN b.name",
            publicationyear=publicationyear):
        publicationyear_list.append(record["b.name"])
        # print("publicationyear_list: ", publicationyear_list)

        # return record["book.name"]

    return publicationyear_list


def print_book_info(tx, book_name):
    publisher_name_list = []
    book_description_list = []

    for record in tx.run(
            "MATCH (b:ΒΟΟΚ {name: $book_name}) "
            "RETURN b.Publisher, b.description",
            book_name=book_name):
        publisher_name_list.append(record["b.Publisher"])
        book_description_list.append((record["b.description"]))
        # print("publisher_name_list: ", publisher_name_list)
        # print("book_description_list: ", book_description_list)

        # return record["book.name"]

    return publisher_name_list, book_description_list


# def print_complete_graph(tx, husband, has_wife, has_written):
#     for record in tx.run("MATCH (a:Person{name: $husband})-[has_written:HAS_WRITTEN{name: $has_written}]->(book:Book)"
#                          "MATCH (a:Person{name: $husband})-[has_wife:HAS_WIFE{name: $has_wife}]->(wife:Person)"
#                          "RETURN wife.name, book.name, has_wife.name, has_written.name ORDER BY book.name",
#                          husband=husband, has_wife=has_wife, has_written=has_written):
#         print("wife: {}, book: {}, has_wife: {}, has_written: {}".format(record["wife.name"], record["book.name"],
#                                                                          record["has_wife.name"],
#                                                                          record["has_written.name"]))
#     return record["wife.name"], record["book.name"], record["has_wife.name"], record["has_written.name"]


# Etsi eftiaksa to query se CYPHER
# MERGE (a:Person{name: "Νίκος Καζαντζάκης"})-[has_written:HAS_WRITTEN{name: "έγραψε"}]->(book:Book{name: "Ο Καπετάν Μιχάλης"})
# MERGE (a)-[has_wife:HAS_WIFE{name: "σύζυγο"}]->(friend:Person{name: "Ελένη Καζαντζάκη"})

# Dictionary of known entities and their corresponding functions
ENTITY_FUNCTION_MAPPING = {
    'Νίκος Καζαντζάκης': 'print_friends',
    'μυθιστορήματα': 'print_books_type',
    'ποιήματα': 'print_books_type',
    'ταξιδιωτικά': 'print_books_type',
    'θεατρικά': 'print_books_type',
    'δοκίμιο': 'print_books_type',
    'TRAVELEDTO': 'print_location_countries',
    'φίλος': 'print_friends_type',
    'συγγενής': 'print_relatives_type',
}

# List of known book titles for fuzzy matching
KNOWN_BOOK_TITLES = [
    'Ο βραχόκηπος',
    'Βίος και πολιτεία του Αλέξη Ζορμπά',
    'Ο Τελευταίος Πειρασμός',
    'Τερτσίνες',
    'Οι Αδερφοφάδες',
    'Ο Φτωχούλης του Θεού',
    'Ταξιδεύοντας: Αγγλία',
    'Χριστόφορος Κολόμβος',
    'Ο Καπετάν Μιχάλης',
    'Ταξιδεύοντας: Ιαπωνία - Κίνα',
    'Σόδομα και Γόμορρα',
    'Ταξιδεύοντας: Ισπανία',
    'Οδύσεια',
    'Ταξιδεύοντας: Ρουσία',
    'Ο Χριστός Ξανασταυρώνεται',
    'Όφις και Κρίνο',
    'Αναφορά στον Γκρέκο',
    'Ο Ανήφορος',
    'Ασκητική - Salvatores dei'
]


def get_relationship(slot_based_query):
    function_to_call = None  # Initialize function_to_call

    driver = GraphDatabase.driver("neo4j://node-3psivztn46ny2.eastus.cloudapp.azure.com:7687",
                                  auth=("neo4j", "P7yK77+(s@#[k"))  # Gia Docker connection
    # print("driver.verify_connectivity(): ", driver.verify_connectivity())
    #
    # print("slot_based_query: ", slot_based_query)

    if isinstance(slot_based_query, list):
        slot_based_query = slot_based_query[0]
    else:
        print("The variable is not a list.")

    # function_to_call = None  # Initialize function_to_call

    # Check if the input is a four-digit year using regex for publication year
    year_pattern = re.match(r'^\d{4}$', slot_based_query)
    if year_pattern:
        # Directly assign the function if it's a year
        function_to_call = 'print_publicationyear'
    else:
        # Use fuzzy matching to find the closest entity
        closest_match, match_score = process.extractOne(slot_based_query, ENTITY_FUNCTION_MAPPING.keys())
        # print("match_score: ", match_score)

        # Fuzzy match against book titles
        title_match, title_score = process.extractOne(slot_based_query, KNOWN_BOOK_TITLES)
        # print("title_score: ", title_score)

        if match_score >= 60 and (match_score >= title_score or title_score < 60):
            # Choose entity function if it has higher or equal score and is above the threshold
            slot_based_query = closest_match
            function_to_call = ENTITY_FUNCTION_MAPPING.get(slot_based_query)
            # print("function_to_call (entity): ", function_to_call)
        elif title_score >= 60:
            # Choose book title function if it has higher score and is above the threshold
            ENTITY_FUNCTION_MAPPING[slot_based_query] = 'print_book_info'
            function_to_call = 'print_book_info'
            slot_based_query = title_match
            # print("function_to_call (book title): ", function_to_call)
        else:
            # print("Δεν βρέθηκε αντιστοίχιση για: ", slot_based_query)
            return []

    # Validation logic to confirm the matched function is appropriate
    if function_to_call not in ['print_friends', 'print_books_type', 'print_location_countries',
                                'print_friends_type', 'print_relatives_type', 'print_publicationyear',
                                'print_book_info']:
        # print(f"The function {function_to_call} may not be suitable for the query: {slot_based_query}")
        return []

    with driver.session() as session:
        if function_to_call == 'print_friends':
            # print("keno")
            # query = session.read_transaction(print_friends, slot_based_query)
            driver.close()
            return []

        elif function_to_call == 'print_books_type':
            # print(f"MPIKE STA {slot_based_query.upper()}!")
            query_count, query_book_names = session.read_transaction(print_books_type, slot_based_query)
            driver.close()
            return query_count, query_book_names

        elif function_to_call == 'print_location_countries':
            query_countries = session.read_transaction(print_location_countries, slot_based_query)
            driver.close()
            return query_countries

        elif function_to_call == 'print_friends_type':
            query_friends = session.read_transaction(print_friends_type, slot_based_query)
            driver.close()
            return query_friends

        elif function_to_call == 'print_relatives_type':
            query_relatives = session.read_transaction(print_relatives_type, slot_based_query)
            driver.close()
            return query_relatives

        elif function_to_call == 'print_publicationyear':
            # print(f"Found a publication year: {slot_based_query}")
            query_publicationyears = session.read_transaction(print_publicationyear, slot_based_query)
            # print("query_publicationyears: ", query_publicationyears)
            driver.close()
            return query_publicationyears

        elif function_to_call == 'print_book_info':
            # print(f"Found a book title: {slot_based_query}")
            query_publisher_name, query_book_description = session.read_transaction(print_book_info, slot_based_query)
            # print("query_publisher_name: ", query_publisher_name)
            # print("query_book_description: ", query_book_description)
            driver.close()
            return query_publisher_name, query_book_description

        else:
            # print("Δεν έχω βάλει ακόμα query για: ", slot_based_query)
            driver.close()
            return []


def has_entity_type(entities, type):
    return any(e for e in entities if e["entity"] == type)


def extract_entity(entities, type1, graph_attr):
    # types = ["married", "wife", "kriti", "vivlio] # enallaktikos tropos diavasmatos twn entities ston parakatw elegxo!
    # p.x. if types[0] and types[1] in query_names:
    # count = 0
    query_names = []
    # Metritis Counter gia na arithmoume ta entities kai na elegxoume ama uparxoun
    for items in entities:
        query_names.append(items["entity"])
        # print(query_names)
        # count += 1
    # print("count: {}".format(count))
    # print("Ta sunolika onomata twn entities einai: {}".format(query_names))
    # print("graph_attr: ", graph_attr)
    # print("graph_attr2: ", graph_attr2)

    # Diladi an den einai empty oi listes logw aniparktwn entities
    # if not len(entities[count-2]['entity']) == 0 and not len(entities[count-1]['entity']) == 0:
    # if entities[count-2] in globals() and entities[count-1] in globals():

    # An uparxoun ta entities "married" kai "wife" dwse tin leksi "Νίκος Καζαντζάκης" gia na mpei sto slot
    # kai na psaksei to sugkekrimeno query
    # if entities[count-2]['entity'] == type1 and entities[count-1]['entity'] == type2:

    if type1 in query_names:
        return graph_attr
    # elif ...
    #     return "Κρήτη"
    else:
        return None

    # if type1 in query_names and type2 not in query_names:
    #     return graph_attr
    # elif type1 in query_names and type2 in query_names:
    #     return graph_attr, graph_attr2
    # # elif ...
    # #     return "Κρήτη"
    # else:
    #     return None

    # return [e["value"] for e in entities if e["entity"] == type][0]


# --------------- ΒΙΒΛΙΑ COUNT QUERY ---------------
class ActionBooksTypeCount(Action):
    def name(self) -> Text:
        return "action_books_type_count"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        entities = tracker.latest_message.get("entities")
        # print("entities: {}".format(entities))

        has_wife1 = has_entity_type(entities, "books_type")
        has_wife2 = has_entity_type(entities, "books_type")
        # print("has_contract_type: {}".format(has_wife1))
        # print("has_device: {}".format(has_wife2))

        books_type_value = tracker.get_slot('books_type')
        # print("relation_value: ", books_type_value)

        if books_type_value is None:  # Diladi an einai empty to list logw aniparktwn entities
            # print("Δεν υπάρχει entity οπότε επιστρέφει None")

            return [SlotSet("books_type", books_type_value)]
            # return []
        else:
            # print("Βρήκε entity-entities και το χρησιμοποιεί για να κάνει query στο γράφο")

            books_type = extract_entity(entities, "books_type", books_type_value)
            # print("extract_entity: {}".format(books_type))

            query_count, query_book_names = get_relationship(books_type)
            # print("query_output: {}".format(query_count))
            # print("query_book_names: {}".format(query_book_names))
            # query_output_complete = get_relationship(wife)
            # print("plan_type: {}".format(query_output_complete))
            # logging.debug(f"wife is {wife}")
            # logging.debug(f"wife is {query_output_complete}")

            return [SlotSet("books_type_count", query_count), SlotSet("books_type", books_type_value)]
            # return []


class ActionUtterGraphOutputBooksTypeCount(Action):
    def name(self) -> Text:
        return "action_utter_graph_output_books_type_count"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        slot_value = tracker.get_slot('books_type_count')

        # Ama den uparxei timi sto slot, tote pes ston xristi na anadiatiposei
        if slot_value is None:
            dispatcher.utter_message(response="utter_rephrase")
        else:
            dispatcher.utter_message(response="utter_books_type_count")

        return [AllSlotsReset()]


# -------- ΤΕΛΟΣ query count βιβλίων --------

# -------- ΑΡΧΗ query ονομάτων βιβλίων --------
class ActionBooksNames(Action):
    def name(self) -> Text:
        return "action_books_names"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        entities = tracker.latest_message.get("entities")
        # print(entities)

        has_wife1 = has_entity_type(entities, "books_type")
        has_wife2 = has_entity_type(entities, "books_type")

        books_type_value = tracker.get_slot('books_type')
        # print("books_type_value: ", books_type_value)

        if books_type_value is None:  # Diladi an einai empty to list logw aniparktwn entities

            return [SlotSet("books_type", books_type_value)]
            # return []
        else:

            books_type = extract_entity(entities, "books_type", books_type_value)

            query_count, query_book_names = get_relationship(books_type)
            # query_output_complete = get_relationship(wife)
            # print("plan_type: {}".format(query_output_complete))
            # logging.debug(f"wife is {wife}")
            # logging.debug(f"wife is {query_output_complete}")

            return [SlotSet("books_names", query_book_names), SlotSet("books_type", books_type_value)]
            # return []


class ActionUtterGraphOutputBooksNames(Action):
    def name(self) -> Text:
        return "action_utter_graph_output_books_names"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        slot_value = tracker.get_slot('books_names')

        # Ama den uparxei timi sto slot, tote pes ston xristi na anadiatiposei
        if slot_value is None:
            dispatcher.utter_message(response="utter_rephrase")
        else:
            dispatcher.utter_message(response="utter_books_names")

        return [AllSlotsReset()]


# -------- ΤΕΛΟΣ query ονομάτων βιβλίων --------


# -------- ΑΡΧΗ query ονομάτων χωρών --------
class ActionLocationCountries(Action):
    def name(self) -> Text:
        return "action_location_countries"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        entities = tracker.latest_message.get("entities")

        # has_wife1 = has_entity_type(entities, "relation")
        # has_wife2 = has_entity_type(entities, 'relation')

        relation_value = tracker.get_slot('relation')

        # if has_wife1 or not has_wife2:
        #     return []

        if relation_value is None:  # Diladi an einai empty to list logw aniparktwn entities

            return [SlotSet("relation", relation_value)]
            # return []
        else:

            relation = extract_entity(entities, "relation", relation_value)

            query_countries = get_relationship(relation)
            # query_output_complete = get_relationship(wife)
            # print("plan_type: {}".format(query_output_complete))
            # logging.debug(f"wife is {wife}")
            # logging.debug(f"wife is {query_output_complete}")

            # Πιστεύω δεν χρειάζεται να αποθηκεύεται το relation slot γιατί δεν θα αξιοποιηθεί μάλλον ως entity σε απαντήσεις
            # return [SlotSet("countries", query_countries), SlotSet("relation", relation_value)]
            return [SlotSet("countries", query_countries)]


class ActionUtterGraphOutputLocationCountries(Action):
    def name(self) -> Text:
        return "action_utter_graph_output_location_countries"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        slot_value = tracker.get_slot('countries')

        # Ama den uparxei timi sto slot, tote pes ston xristi na anadiatiposei
        if slot_value is None:
            dispatcher.utter_message(response="utter_rephrase")
        else:
            dispatcher.utter_message(response="utter_location_countries")

        return [AllSlotsReset()]


# -------- ΑΡΧΗ query ονομάτων φίλων --------
class ActionFriendsNames(Action):
    def name(self) -> Text:
        return "action_friends_names"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        entities = tracker.latest_message.get("entities")
        # print(entities)

        # has_wife1 = has_entity_type(entities, "type")
        # has_wife2 = has_entity_type(entities, 'type')

        type_value = tracker.get_slot('type')
        # print(type_value)

        # if has_wife1 or not has_wife2:
        #     return []

        if type_value is None:  # Diladi an einai empty to list logw aniparktwn entities

            return [SlotSet("type", type_value)]
            # return []
        else:

            type = extract_entity(entities, "type", type_value)
            # print(type)

            query_type = get_relationship(type)
            # print(query_type)
            # query_output_complete = get_relationship(wife)
            # print("plan_type: {}".format(query_output_complete))
            # logging.debug(f"wife is {wife}")
            # logging.debug(f"wife is {query_output_complete}")

            # Πιστεύω δεν χρειάζεται να αποθηκεύεται το relation slot γιατί δεν θα αξιοποιηθεί μάλλον ως entity σε απαντήσεις
            # return [SlotSet("countries", query_countries), SlotSet("relation", relation_value)]
            return [SlotSet("friends_names", query_type)]


class ActionUtterGraphOutputFriendsNames(Action):
    def name(self) -> Text:
        return "action_utter_graph_output_friends_names"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        slot_value = tracker.get_slot('friends_names')
        # print("friends names slot value: ", slot_value)

        # Ama den uparxei timi sto slot, tote pes ston xristi na anadiatiposei
        if slot_value is None:
            dispatcher.utter_message(response="utter_rephrase")
        else:
            dispatcher.utter_message(response="utter_friends_names")

        return [AllSlotsReset()]


# -------- ΑΡΧΗ query ονομάτων συγγενών --------
class ActionRelativesNames(Action):
    def name(self) -> Text:
        return "action_relatives_names"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        entities = tracker.latest_message.get("entities")
        # print(entities)

        # has_wife1 = has_entity_type(entities, "type")
        # has_wife2 = has_entity_type(entities, 'type')

        type_value = tracker.get_slot('type')
        # print(type_value)

        # if has_wife1 or not has_wife2:
        #     return []

        if type_value is None:  # Diladi an einai empty to list logw aniparktwn entities

            return [SlotSet("type", type_value)]
            # return []
        else:

            type = extract_entity(entities, "type", type_value)
            # print(type)

            query_type = get_relationship(type)
            # print(query_type)
            # query_output_complete = get_relationship(wife)
            # print("plan_type: {}".format(query_output_complete))
            # logging.debug(f"wife is {wife}")
            # logging.debug(f"wife is {query_output_complete}")

            # Πιστεύω δεν χρειάζεται να αποθηκεύεται το relation slot γιατί δεν θα αξιοποιηθεί μάλλον ως entity σε απαντήσεις
            # return [SlotSet("countries", query_countries), SlotSet("relation", relation_value)]
            return [SlotSet("relatives_names", query_type)]


class ActionUtterGraphOutputRelativesNames(Action):
    def name(self) -> Text:
        return "action_utter_graph_output_relatives_names"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        slot_value = tracker.get_slot('relatives_names')
        # print("relatives_names slot value: ", slot_value)

        # Ama den uparxei timi sto slot, tote pes ston xristi na anadiatiposei
        if slot_value is None:
            dispatcher.utter_message(response="utter_rephrase")
        else:
            dispatcher.utter_message(response="utter_relatives_names")

        return [AllSlotsReset()]


# -------- ΑΡΧΗ query ονομάτων βιβλίων από ημερομηνίες έκδοσης publication year --------
class ActionPublicationyearBookNames(Action):
    def name(self) -> Text:
        return "action_publicationyear_book_names"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        entities = tracker.latest_message.get("entities")
        # print("entities: ", entities)

        # has_wife1 = has_entity_type(entities, "type")
        # has_wife2 = has_entity_type(entities, 'type')

        book_publication_year_value = tracker.get_slot('book_publication_year')
        # print(book_publication_year_value)

        # if has_wife1 or not has_wife2:
        #     return []

        if book_publication_year_value is None:  # Diladi an einai empty to list logw aniparktwn entities

            return [SlotSet("book_publication_year", book_publication_year_value)]
            # return []
        else:

            book_publication_year = extract_entity(entities, "book_publication_year", book_publication_year_value)
            # print("book_publication_year: ", book_publication_year)

            query_type = get_relationship(book_publication_year)
            # print("query_type: ", query_type)
            # query_output_complete = get_relationship(wife)
            # print("plan_type: {}".format(query_output_complete))
            # logging.debug(f"wife is {wife}")
            # logging.debug(f"wife is {query_output_complete}")

            # Πιστεύω δεν χρειάζεται να αποθηκεύεται το relation slot γιατί δεν θα αξιοποιηθεί μάλλον ως entity σε απαντήσεις
            # return [SlotSet("countries", query_countries), SlotSet("relation", relation_value)]
            return [SlotSet("books_names", query_type), SlotSet("book_publication_year", book_publication_year_value)]


class ActionUtterGraphOutputPublicationyearBookNames(Action):
    def name(self) -> Text:
        return "action_utter_graph_output_publicationyear_book_names"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        books_names = tracker.get_slot('books_names')
        # print("publicationyear_book_names slot value: ", books_names)

        book_publication_year = tracker.get_slot('book_publication_year')

        # Ama den uparxei timi sto slot, tote pes ston xristi na anadiatiposei
        # Ελέγχω και για άδεια λίστα γιατί μερικά slots είναι lists
        if (books_names is None or books_names == []) and book_publication_year is not None:
            dispatcher.utter_message(
                f"📁-> Φαίνεται ότι δεν υπάρχουν διαθέσιμα βιβλία στη βάση δεδομένων γράφου για το έτος {book_publication_year}.")
        elif books_names is None or books_names == []:
            dispatcher.utter_message(response="utter_rephrase")
        else:
            dispatcher.utter_message(response="utter_publicationyear_book_names")

        return [AllSlotsReset()]


# -------- ΑΡΧΗ query ονομάτων βιβλίων από ημερομηνίες έκδοσης publication year --------
class ActionBookInfo(Action):
    def name(self) -> Text:
        return "action_book_info"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        entities = tracker.latest_message.get("entities")
        # print("entities: ", entities)

        # has_wife1 = has_entity_type(entities, "type")
        # has_wife2 = has_entity_type(entities, 'type')

        book_name_single_text = tracker.get_slot('book_name_single_text')
        # print(book_name_single_text)

        # if has_wife1 or not has_wife2:
        #     return []

        if book_name_single_text is None:  # Diladi an einai empty to list logw aniparktwn entities

            return [SlotSet("book_name_single_text", book_name_single_text)]
            # return []
        else:

            book_name_single_text = extract_entity(entities, "book_name_single_text", book_name_single_text)
            # print("book_name_single_text: ", book_name_single_text)

            books_publisher_name, book_description = get_relationship(book_name_single_text)
            # print("query_type1: ", books_publisher_name)
            # print("query_type2:", book_description)

            # books_names = extract_entity(entities, "books_names", books_names_value)
            # print("books_names: ", books_names)
            #
            # query_type2 = get_relationship(book_description)
            # print("query_type: ", query_type2)

            # query_output_complete = get_relationship(wife)
            # print("plan_type: {}".format(query_output_complete))
            # logging.debug(f"wife is {wife}")
            # logging.debug(f"wife is {query_output_complete}")

            # Πιστεύω δεν χρειάζεται να αποθηκεύεται το relation slot γιατί δεν θα αξιοποιηθεί μάλλον ως entity σε απαντήσεις
            # return [SlotSet("countries", query_countries), SlotSet("relation", relation_value)]
            return [SlotSet("book_name_single_text", book_name_single_text),
                    SlotSet("books_publisher_name", books_publisher_name),
                    SlotSet("book_description", book_description)]


class ActionUtterGraphOutputPublisherName(Action):
    def name(self) -> Text:
        return "action_utter_graph_output_publisher_name"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        book_name_single_text = tracker.get_slot('book_name_single_text')
        # print("publicationyear_book_names slot value: ", book_name_single_text)

        books_publisher_name = tracker.get_slot('books_publisher_name')

        # Ama den uparxei timi sto slot, tote pes ston xristi na anadiatiposei
        # Ελέγχω και για άδεια λίστα γιατί μερικά slots είναι lists
        if (book_name_single_text is None or book_name_single_text == []) and books_publisher_name is not None:
            dispatcher.utter_message(
                f"📁-> Φαίνεται ότι δεν υπάρχουν διαθέσιμα βιβλία στη βάση δεδομένων γράφου για τον εκδότη {books_publisher_name}.")
        elif book_name_single_text is None or book_name_single_text == []:
            dispatcher.utter_message(response="utter_rephrase")
        else:
            dispatcher.utter_message(response="utter_publisher_names")

        return [AllSlotsReset()]


class ActionUtterGraphOutputBookDescription(Action):
    def name(self) -> Text:
        return "action_utter_graph_output_book_description"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        book_name_single_text = tracker.get_slot('book_name_single_text')
        # print("book_name_single_text slot value: ", book_name_single_text)

        book_description = tracker.get_slot('book_description')
        # print("book_description: ", book_description)

        # Ama den uparxei timi sto slot, tote pes ston xristi na anadiatiposei
        # Ελέγχω και για άδεια λίστα γιατί μερικά slots είναι lists
        if (book_description == [None] or book_description == []) and (book_name_single_text != []):
            dispatcher.utter_message(
                f"📁-> Φαίνεται ότι δεν υπάρχει διαθέσιμη περιγραφή για το βιβλίο {book_name_single_text}.")
        # elif book_description is None or book_description == []:
        #     dispatcher.utter_message(response="utter_rephrase")
        else:
            dispatcher.utter_message(response="utter_book_description")

        return [AllSlotsReset()]


# -------- ΤΕΛΟΣ query ονομάτων χωρών --------


# -------- ΑΡΧΗ query ονομάτων πόλεων και περιοχών --------
# class ActionLocationAreas(Action):
#     def name(self) -> Text:
#         return "action_location_areas"
#
#     def run(
#             self,
#             dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any],
#     ) -> List[Dict[Text, Any]]:
#
#         entities = tracker.latest_message.get("entities")
#         print("entities: {}".format(entities))
#
#         has_wife1 = has_entity_type(entities, "relation")
#         has_wife2 = has_entity_type(entities, 'location_type')
#         print("has_contract_type: {}".format(has_wife1))
#         print("has_device: {}".format(has_wife2))
#
#         relation_value = tracker.get_slot('relation')
#         print("relation_value: ", relation_value)
#
#         location_type_value = tracker.get_slot('location_type')
#         print("location_type_value: ", location_type_value)
#
#         # if has_wife1 or not has_wife2:
#         #     return []
#
#         if relation_value is None and location_type_value is None:  # Diladi an einai empty to list logw aniparktwn entities
#             print("Δεν υπάρχει entity οπότε επιστρέφει None")
#
#             # Δηλαδή επέστρεψε None
#             return [SlotSet("relation", relation_value), SlotSet("location_type", location_type_value)]
#             # return []
#         else:
#             print("Βρήκε entity-entities και το χρησιμοποιεί για να κάνει query στο γράφο")
#
#             # Να δω πως θα διαχειριστώ 2+ slots σε κάθε function
#             relation = extract_entity(entities, "relation", "location_type", relation_value, location_type_value)
#             print("extract_entity: {}".format(relation))
#
#             query_countries = get_relationship(relation)
#             print("query_output: {}".format(query_countries))
#             # query_output_complete = get_relationship(wife)
#             # print("plan_type: {}".format(query_output_complete))
#             # logging.debug(f"wife is {wife}")
#             # logging.debug(f"wife is {query_output_complete}")
#
#             # Πιστεύω δεν χρειάζεται να αποθηκεύεται το relation slot γιατί δεν θα αξιοποιηθεί μάλλον ως entity σε απαντήσεις
#             # return [SlotSet("countries", query_countries), SlotSet("relation", relation_value)]
#             return [SlotSet("location_names", query_countries)]
#
#
# class ActionUtterGraphOutputLocationAreas(Action):
#     def name(self) -> Text:
#         return "action_utter_graph_output_location_areas"
#
#     def run(
#             self,
#             dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any],
#     ) -> List[Dict[Text, Any]]:
#
#         slot_value = tracker.get_slot('location_names')
#         print("To slot value για εύρεση στο γράφο είναι: {}\n".format(slot_value))
#
#         # Ama den uparxei timi sto slot, tote pes ston xristi na anadiatiposei
#         if slot_value is None:
#             dispatcher.utter_message(response="utter_rephrase")
#         else:
#             dispatcher.utter_message(response="utter_location_names")
#
#         return []

# -------- ΤΕΛΟΣ query πόλεων και περιοχών --------


class ActionSetReminder(Action):
    """Schedules a reminder, supplied with the last message's entities."""

    def name(self) -> Text:
        return "action_set_reminder"

    async def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # dispatcher.utter_message("Θα σε υπενθυμίσω 25 δευτερόλεπτα.")

        date = datetime.datetime.now() + datetime.timedelta(seconds=240)
        # entities = tracker.latest_message.get("entities")

        reminder = ReminderScheduled(
            "EXTERNAL_reminder",
            trigger_date_time=date,
            # entities=entities,
            name="my_reminder",
            kill_on_user_message=True,  # Whether a user message before the trigger time will abort the reminder
        )

        return [reminder]


class ActionReactToReminder(Action):
    """Reminds the user with his name when idle."""

    def name(self) -> Text:
        return "action_react_to_reminder"

    async def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        text_list = ["Μας ξέχασες!",
                     "Είσαι ακόμα εδώ; Αν όχι, σε περιμένουμε στο μουσείο!",
                     "Είμαι εδώ ακόμα, έτοιμος να ακούσω περισσότερα από εσένα!",
                     "Είμαι εδώ ακόμα, έλα να συνεχίσουμε την κουβέντα μας!",
                     "Αν υπάρχει κάτι που θέλεις να συζητήσουμε, είμαι εδώ για να σε βοηθήσω!"]

        random_text = random.choice(text_list)

        dispatcher.utter_message(random_text)

        return []


class ActionGoodbye(Action):
    """Goodbyes the user with his name."""

    def name(self) -> Text:
        return "action_goodbye"

    async def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        text_list = ["Αντίο, σε ευχαριστούμε για την επίσκεψη. 🙂",
                     "Αντίο, θα σε περιμένουμε στο Μουσείο. 🙂"]

        random_text = random.choice(text_list)

        dispatcher.utter_message(random_text)

        return []


class ActionCreateDenyCarousels(Action):
    def name(self) -> Text:
        return "action_create_deny_carousels"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        message = {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements": [
                    {
                        "title": "Σχολικά χρόνια",
                        "subtitle": "Πρόγραμμα από την μαθητική παράσταση Οιδίπους Τύραννος",
                        "image_url": "https://www.memobot.eu/wp-content/uploads/2022/10/schoolyears.jpg",
                        "buttons": [
                            {
                                "title": "Μάθε περισσότερα",
                                "payload": "Σχολικά χρόνια",
                                "type": "postback"
                            }
                        ]
                    },
                    {
                        "title": "Οικογένεια",
                        "subtitle": "Με την μητέρα και τις αδερφές του Αναστασία και Ελένη",
                        "image_url": "https://www.memobot.eu/wp-content/uploads/2022/10/family.jpg",
                        "buttons": [
                            {
                                "title": "Μάθε περισσότερα",
                                "payload": "Οικογένεια",
                                "type": "postback"
                            }
                        ]
                    },
                    {
                        "title": "Σπίτι",
                        "subtitle": "Το σπίτι όπου γεννήθηκε ο ΝΚ στο Ηράκλειο",
                        "image_url": "https://www.memobot.eu/wp-content/uploads/2022/10/house.jpg",
                        "buttons": [
                            {
                                "title": "Μάθε περισσότερα",
                                "payload": "Οικία Καζαντζακη",
                                "type": "postback"
                            }
                        ]
                    },
                ]
            }
        }

        dispatcher.utter_message(attachment=message)

        dispatcher.utter_message(text="Ωραία, μπορείς να με ρωτήσεις κάτι από τα παραπάνω θέματα ή να μου κάνεις "
                                      "μια δική σου ερώτηση σχετικά με την ζωή και το έργο του Νίκου Καζαντζάκη! 😃")

        return []


class ActionCreateWelcomeCarousels(Action):
    def name(self) -> Text:
        return "action_create_welcome_carousels"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        message = {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements": [
                    {
                        "subtitle": "Η ζωή",
                        "image_url": "https://www.memobot.eu/wp-content/uploads/2022/10/schoolyears.jpg",
                        "buttons": [
                            {
                                "title": "Ο συγγραφέας",
                                "payload": "/works",
                                "type": "postback"
                            },
                            {
                                "title": "Η οικογένεια",
                                "payload": "/family",
                                "type": "postback"
                            },
                            {
                                "title": "Οι φίλοι ",
                                "payload": "Ποιοι είναι οι φίλοι του Νίκου Καζαντζάκη",
                                "type": "postback"
                            }
                        ]
                    },
                    {
                        "subtitle": "Το έργο",
                        "image_url": "https://www.memobot.eu/wp-content/uploads/2022/10/family.jpg",
                        "buttons": [
                            {
                                "title": "Μυθιστορήματα",
                                "payload": "Ποια μυθιστορήματα έγραψε ο Νίκος Καζαντζάκης;",
                                "type": "postback"
                            },
                            {
                                "title": "Ταξιδιωτικά",
                                "payload": "Ποια ταξιδιωτικά βιβλία συνολικά υπάρχουν από τον Καζαντζάκη;",
                                "type": "postback"
                            },
                            {
                                "title": "Ποίηση",
                                "payload": "Ονομασίες των ποιημάτων",
                                "type": "postback"
                            }
                        ]
                    },
                ]
            }
        }

        dispatcher.utter_message(attachment=message)

        dispatcher.utter_message(text="Καλώς ήρθατε στον ψηφιακό βοηθό για την ζωή και το έργο του Νίκου Καζαντζάκη. "
                                      "Εδώ θα ανακαλύψετε άγνωστες πτυχές της ζωής του μεγάλου συγγραφέα καθώς και λεπτομέρειες για τα βιβλία και τα άλλα γραπτά του έργα. "
                                      "Ένας έξυπνος γράφος γνώσης είναι συνδεδεμένος με τον ψηφιακό βοηθό για την παροχή πιο εξειδικευμένων πληροφοριών.")

        return []


class ActionGetNikosKazantzakisOccupations(Action):
    def name(self) -> Text:
        return "action_get_nikos_kazantzakis_occupations"

    def run(self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # SPARQL query to get the occupations in Greek
        query = """
        SELECT ?occupation ?occupationLabel WHERE {
            wd:Q214622 wdt:P106 ?occupation.  # Q214622 = Nikos Kazantzakis, P106 = occupation
            SERVICE wikibase:label { bd:serviceParam wikibase:language "el". }  # Set language to Greek
        }
        """
        # Define the endpoint for Wikidata's SPARQL query service
        endpoint_url = "https://query.wikidata.org/sparql"
        headers = {
            "Accept": "application/json"
        }

        # Send the request
        response = requests.get(endpoint_url, params={'query': query}, headers=headers)

        if response.status_code == 200:
            data = response.json()
            occupations = []

            # Extract occupations from the JSON response
            for item in data['results']['bindings']:
                occupation_label = item['occupationLabel']['value']
                occupations.append(occupation_label)

            if occupations:
                dispatcher.utter_message(
                    text="🌐-> Οι επαγγελματικές ασχολίες του Νίκου Καζαντζάκη είναι: " + ", ".join(occupations))
            else:
                dispatcher.utter_message(text="🌐-> Δεν βρέθηκαν επαγγελματικές ασχολίες για τον Νίκο Καζαντζάκη.")
        else:
            dispatcher.utter_message(text="🌐-> Παρουσιάστηκε πρόβλημα κατά την ανάκτηση των στοιχείων.")

        return []


class ActionGetKazantzakisNobelNominations(Action):
    def name(self) -> Text:
        return "action_get_kazantzakis_nobel_nominations"

    def run(self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # SPARQL query to get nomination years in Greek
        query = """
        SELECT DISTINCT ?year WHERE {
          wd:Q214622 p:P1411 ?nominationStatement.     # Q214622 = Nikos Kazantzakis, P1411 = nominated for
          ?nominationStatement ps:P1411 wd:Q37922;     # ps:P1411 is the nomination, Q37922 = Nobel Prize in Literature
                                pq:P585 ?date.         # P585 = point in time (date of nomination)

          BIND(YEAR(?date) AS ?year)                    # Extract year from the date

          SERVICE wikibase:label { bd:serviceParam wikibase:language "el". }  # Set language to Greek
        }
        """
        # Define the endpoint for Wikidata's SPARQL query service
        endpoint_url = "https://query.wikidata.org/sparql"
        headers = {
            "Accept": "application/json"
        }

        # Send the request
        response = requests.get(endpoint_url, params={'query': query}, headers=headers)

        if response.status_code == 200:
            data = response.json()
            years = []

            # Extract nomination years from the JSON response
            for item in data['results']['bindings']:
                year = item['year']['value']
                years.append(year)

            if years:
                dispatcher.utter_message(
                    text="🌐-> Ο Νίκος Καζαντζάκης ήταν υποψήφιος για το Νόμπελ Λογοτεχνίας 9 φορές, τα έτη: " + ", ".join(
                        years) + ". Τελικά δεν βραβεύτηκε ποτέ.")
            else:
                dispatcher.utter_message(
                    text="🌐-> Δεν βρέθηκαν πληροφορίες για υποψηφιότητες του Νίκου Καζαντζάκη για το Νόμπελ Λογοτεχνίας.")
        else:
            dispatcher.utter_message(text="🌐-> Παρουσιάστηκε πρόβλημα κατά την ανάκτηση των στοιχείων.")

        return []

class ActionDefaultFallback(Action):

    def name(self) -> Text:
        return "action_default_fallback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_query = tracker.latest_message.get("text")
        # Call your RAG model API
        rag_response = utils.get_rag_response(user_query)

        # Send the response back to the user
        dispatcher.utter_message(text=rag_response)

        return []