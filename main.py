import streamlit as st
import json
from trie_node import Trie

@st.cache_data
def import_data(filename):
    with open(filename) as file:
        content = file.read()
    output = json.loads(content)
    return output

@st.cache_data
def insert_trie(data):
    trie = Trie()
    for i in range(0, len(data)):
        trie.insert(data[i])   
    return trie

def collect_data():
    if "autosuggest_occ_names" not in st.session_state:
        st.session_state.autosuggest_occupations = import_data("occ_names_jt.json")
        st.session_state.autosuggest_keywords = import_data("keywords_skills.json")
        st.session_state.autosuggest_skills = import_data("competences.json")
        st.session_state.autosuggest_groups = import_data("syn_occ_group_titles.json")
        st.session_state.names_weights = import_data("names_weights.json")
        st.session_state.names_id = import_data("names_id.json")
        st.session_state.id_names_preferred_label = import_data("id_preferred_labels.json")
        st.session_state.id_fields = import_data("id_occupation_fields.json")
        st.session_state.id_names_related = import_data("id_names_related.json")
        st.session_state.id_names_type = import_data("id_names_type.json")
        st.session_state_symbols = import_data("symbols.json")

        st.session_state.trie_occupations = insert_trie(st.session_state.autosuggest_occupations)
        st.session_state.trie_keywords = insert_trie(st.session_state.autosuggest_keywords)
        st.session_state.trie_skills = insert_trie(st.session_state.autosuggest_skills)
        st.session_state.trie_groups = insert_trie(st.session_state.autosuggest_groups)

        st.session_state.occupations_response = []
        st.session_state.keywords_response = []
        st.session_state.skills_response = []
        st.session_state.groups_response = []

def show_initial_information():
    st.title("Autosuggest")
    initial_text = "Vill du starta om tryck cmd + r"
    st.markdown(f"<p style='font-size:12px;'>{initial_text}</p>", unsafe_allow_html=True)

def sort_response_based_on_weight(response):
    response = {key: value for (key, value) in st.session_state.names_weights.items() if key in response}
    response = dict(sorted(response.items(), key = lambda x:x[1], reverse = True))
    response = list(response.keys())[0:20]
    return response

def generate_response(letters):
    response_occupations = st.session_state.trie_occupations.starts_with(letters.lower())
    response_keywords = st.session_state.trie_keywords.starts_with(letters.lower())
    response_skills = st.session_state.trie_skills.starts_with(letters.lower())
    response_groups = st.session_state.trie_groups.starts_with(letters.lower())

    st.session_state.occupations_response = sort_response_based_on_weight(response_occupations)
    st.session_state.keywords_response = sort_response_based_on_weight(response_keywords)
    st.session_state.skills_response = sort_response_based_on_weight(response_skills)
    st.session_state.groups_response = sort_response_based_on_weight(response_groups)

def add_symbols_to_related(related):
    related_with_symbols = []
    for r in related:
        r = r.replace('+', '')
        id = st.session_state.names_id.get(r.lower())
        field = st.session_state.id_fields.get(id)[0]
        symbol = st.session_state_symbols.get(field)
        related_with_symbols.append(f"{symbol} {r}")
    return related_with_symbols

def add_symbols_to_fields(data):
    related_with_symbols = {}
    for key, value in data.items():
        symbol = st.session_state_symbols.get(key)
        new_key = f"{symbol} {key}"
        related_with_symbols[new_key] = value
    return related_with_symbols    

def print_alternatives(max_occupations, max_keywords, max_skills, max_groups):

    if max_occupations > 0:
        occupations = []
        for v in range(max_occupations):
            if v < len(st.session_state.occupations_response):
                name = st.session_state.occupations_response[v]
                id = st.session_state.names_id.get(name)
                preferred_label = st.session_state.id_names_preferred_label.get(id)
                type = st.session_state.id_names_type.get(id)
                weight = st.session_state.names_weights.get(name)
                if not type == "job-title":
                    #field = st.session_state.id_fields.get(id)[0]
                    #symbol = st.session_state_symbols.get(field)
                    showname = f"{preferred_label} ({weight})"
                    occupations.append(showname)
                else:
                    related_occupation = st.session_state.id_names_related.get(id)[0]
                    id_related = st.session_state.names_id.get(related_occupation.lower())
                    #field = st.session_state.id_fields.get(id_related)[0]
                    showname = f"{related_occupation} / {preferred_label} ({weight})"
                    occupations.append(showname)

        st.write("Yrkesbenämningar och jobtitlar")
        st.write(occupations)

    if max_keywords > 0:
        keywords = []
        for v in range(max_keywords):
            if v < len(st.session_state.keywords_response):            
                name = st.session_state.keywords_response[v]
                id = st.session_state.names_id.get(name)
                preferred_label = st.session_state.id_names_preferred_label.get(id)
                weight = st.session_state.names_weights.get(name)
                related = st.session_state.id_names_related.get(id)
                #related = add_symbols_to_related(related)
                #symbol = st.session_state_symbols.get("Nyckelord")
                showname = f"{preferred_label} ({weight})"
                keywords.append(showname)
                keywords.append(related)

        st.write("Nyckelord")
        st.write(keywords)

    if max_skills > 0:
        skills = []
        for v in range(max_keywords):
            if v < len(st.session_state.skills_response):
                name = st.session_state.skills_response[v]
                id = st.session_state.names_id.get(name)
                preferred_label = st.session_state.id_names_preferred_label.get(id)
                weight = st.session_state.names_weights.get(name)
                related = st.session_state.id_names_related.get(id)
                #related = add_symbols_to_related(related)
                #symbol = st.session_state_symbols.get("Kompetensbegrepp")
                showname = f"{preferred_label} ({weight})"
                skills.append(showname)
                skills.append(related)

        st.write("Kompetensbegrepp")
        st.write(skills)

    if max_groups > 0:
        groups = []
        for v in range(max_keywords):
            if v < len(st.session_state.groups_response):
                name = st.session_state.groups_response[v]
                id = st.session_state.names_id.get(name)
                preferred_label = st.session_state.id_names_preferred_label.get(id)
                weight = st.session_state.names_weights.get(name)
                related = st.session_state.id_names_related.get(id)
                #symbol = st.session_state_symbols.get("Grupperande yrkesbegrepp")
                showname = f"{preferred_label} ({weight})"
                groups.append(showname)
                #related = add_symbols_to_fields(related)
                groups.append(related)

        st.write("Grupperande yrkesbegrepp")
        st.write(groups)

def test_autosuggest():

    col1, col2 = st.columns(2)

    with col1:
        max_occupations = st.slider("Antal yrkesbegrepp", 0, 20, 4)
        max_keywords = st.slider("Antal nyckelbegrepp", 0, 10, 2)

    with col2:
        max_skills = st.slider("Antal kompetensbegrepp", 0, 10, 2)
        max_groups = st.slider("Antal grupperande yrkesbegrepp", 0, 10, 2)


    selected_letters = st.text_input("Yrkessök")

    if selected_letters:
        generate_response(selected_letters)
        print_alternatives(max_occupations, max_keywords, max_skills, max_groups)
    
def main():
    collect_data()
    show_initial_information()
    test_autosuggest()

if __name__ == '__main__':
    main()