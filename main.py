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
def insert_trie():
    trie = Trie()
    words = st.session_state.autosuggest_names
    for i in range(0, len(words)):
        trie.insert(words[i])   
    return trie

def hämta_hem_data():
    if "autosuggest_names" not in st.session_state:
        st.session_state.autosuggest_names = import_data("alla_namn.json")
        st.session_state.name_weight = import_data("namn_vikt.json")
        st.session_state.name_id = import_data("namn_id.json")
        st.session_state.id_type = import_data("id_type.json")
        st.session_state.id_related = import_data("id_related.json")
        st.session_state.id_fields = import_data("id_fields.json")
        st.session_state.trie = insert_trie()
        st.session_state.svar = []

def show_initial_information():
    st.title("Autosuggest")
    initial_text = "Vill du starta om tryck cmd + r"
    st.markdown(f"<p style='font-size:12px;'>{initial_text}</p>", unsafe_allow_html=True)

def generera_lista(bokstäver):
    svar = st.session_state.trie.starts_with(bokstäver.lower())
    viktat_svar = {key: value for (key, value) in st.session_state.name_weight.items() if key in svar}
    viktat_svar = dict(sorted(viktat_svar.items(), key = lambda x:x[1], reverse = True))
    viktat_svar = list(viktat_svar.keys())[0:20]
    st.session_state.svar = viktat_svar

def skriv_ut_alternativ():
    #grupplista = []
    yrkeslista = []
    nyckelordslista = []
    for v in st.session_state.svar:
        id = st.session_state.name_id.get(v)
        typ = st.session_state.id_type.get(id)
        vikt = st.session_state.name_weight.get(v)

        if typ == "group-title" or typ == "keyword":
            nyckelordslista.append(f"{v}({typ}) {vikt}")
            nyckelordslista.append(st.session_state.id_related.get(id))

        elif typ == "occupation-name":
            yrkeslista.append(f"{v}({typ}) {vikt}")

        elif typ == "job-title":
            relaterad = st.session_state.id_related.get(id)[0]
            yrkeslista.append(f"{v}({relaterad}) {vikt}")

        elif typ == "skill":
            nyckelordslista.append(f"{v}({typ}) {vikt}")
            nyckelordslista.append(st.session_state.id_related.get(id))
                       
        elif typ == "synonym-skill":
            nyckelordslista.append(f"{v}({typ}) {vikt}")
            nyckelordslista.append(st.session_state.id_related.get(id))
    
    yrkeslista = yrkeslista[0:5]
    nyckelordslista = nyckelordslista[0:10]

    #st.write(grupplista)
    st.write("Yrkesbenämningar och jobtitlar")
    st.write(yrkeslista)
    st.write("Grupperande begrepp")
    st.write(nyckelordslista)


def testa_autosuggest():
    bokstäver = st.text_input("Yrkessök")

    if bokstäver:
        generera_lista(bokstäver)
        skriv_ut_alternativ()
    
def main():
    hämta_hem_data()
    show_initial_information()
    testa_autosuggest()

if __name__ == '__main__':
    main()