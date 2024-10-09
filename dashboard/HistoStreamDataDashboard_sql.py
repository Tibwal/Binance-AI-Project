import pandas as pd
import pymysql
from sqlalchemy import create_engine
import streamlit as st
import plotly.graph_objects as go
import pymongo
import time
from time import sleep
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime as dt
import subprocess

# Connexion à la base de données MySQL
db_connection = create_engine("mysql+pymysql://opa_user:opa_pwd@db_mysql/opa_db")


@st.cache_data
def retrieve_data_from_db(symbol_id, granularity_id, start_date, end_date):
    query = """
    SELECT * FROM history_Data 
    WHERE symbol_id = %s AND granularity_id = %s AND close_time BETWEEN %s AND %s
    """
    df = pd.read_sql(query, con=db_connection, params=(symbol_id, granularity_id, start_date, end_date))
    return df



@st.cache_data
def create_candlestick_chart(df):
    fig = go.Figure(data=[go.Candlestick(
                        x=df['close_time'],
                        open=df['open'],
                        high=df['high'],
                        low=df['low'],
                        close=df['close']
                        )
                        ]
                    )
    fig.update_layout(xaxis_rangeslider_visible=False)
    return fig

@st.cache_data
def create_candlestick_chart_MongoDB(df):
    fig = go.Figure(data=[go.Candlestick(
                        x=df['date'],
                        open=df['open'],
                        high=df['high'],
                        low=df['low'],
                        close=df['close']
                        )
                        ]
                    )
    fig.update_layout(xaxis_rangeslider_visible=False)
    return fig

# Configuration de l'application Streamlit
st.set_page_config(
    page_title='💰 📈 🚀 OPA project 💰 📈 🚀',
    page_icon='📈',
    layout='wide'
)
title, image = st.columns(2)

with title:
    st.title("💰 📈 🚀 OPA project 💰 📈 🚀")
        
with image:
    st.image("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcWNkNXVsNGI4em80ZGFlZnMzb3MyeHB2YnY2OGd4Y2o2ZGlyaHNldSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/nguei03gAsnJzinNto/giphy.gif",
    width=200)

st.write('''Bienvenue dans le tableau de bord du projet OPA (Opérations sur Actifs) 💰 📈 🚀 ! \n
Cette application vous permet d'explorer et d'analyser les données historiques des actifs 
financiers avec des graphiques interactifs en chandeliers.\n
De plus, elle offre un aperçu des données en streaming pour suivre les tendances en temps réel.\n
Elle propose aussi un modèle prédictif pour anticiper les mouvements futurs du marché.''')

# Onglets pour différents tableaux de bord
tab00, tab11, tab22 = st.tabs(["Tableau de bord des données historiques", "Tableau de bord des données en streaming", "Tableau de bord du modèle prédictif"])

with tab00:
    
    st.title('Tableau de bord des données historiques')
    
    col001, col002 = st.columns(2)
    symbol_id_vals = [1, 2]
    granularity_id_vals = [1, 2]

    # Widgets pour les filtres
    symbol_id = col001.selectbox("Sélectionnez une valeur pour l'ID du symbole (Choisissez 1 pour BTCEUR te 2 pour ETHEUR) ", symbol_id_vals, key='symbol_id_00')
    granularity_id = col002.selectbox("Sélectionnez une valeur pour l'ID de granularité (Choisissez 1 ou 2 pour une granularité de 1 heure et 1 jour)", granularity_id_vals, key='granularity_id_00')

    # Widgets pour la sélection de la fenêtre de dates
    col003, col004 = st.columns(2)
    start_date = col003.date_input("Date de début", value=pd.to_datetime('2024-04-01'), key='start_date_00')
    end_date = col004.date_input("Date de fin", value=pd.to_datetime('2024-05-31'), key='end_date_00')

    if st.button("Filtrer et afficher le graphique", key='filter_button_00'):
        # Récupération et affichage des données en fonction des filtres
        df = retrieve_data_from_db(symbol_id, granularity_id, start_date, end_date)

        st.markdown('### DataFrame filtré')
        st.write(df)

        st.markdown('### Graphique en chandeliers 📈')
        fig = create_candlestick_chart(df)
        st.plotly_chart(fig, use_container_width=True)

with tab11:
    st.title('Tableau de bord des données en streaming BTCEUR')
    st.markdown("**Onglet encore en construction**")
    @st.cache_resource
    def init_connection():
        return pymongo.MongoClient("mongodb://admin:pass@db_mongodb:27017/")
    client = init_connection()
    ##client = pymongo.MongoClient("mongodb://admin:pass@db_mongodb:27017/")
    db = client.OPA_MongoDB

    
    if st.button("Afficher le graphique des données streaming", key='filter_button_11'):
        placeholder = st.empty()
        while True :
            with placeholder.container():
                @st.cache_data(ttl=61)
                def get_btcData():
                    collection = db['CandlessticksCollection'].find({})
                    return pd.DataFrame(collection)

                # Retrieve data from Mongodb database
                data_stream = get_btcData()
                #data_stream =data_stream.drop(['_id', 'timestamp','high','low'], axis=1)

                # Display data
                st.markdown('### Données collectées depuis Websocket Binance et stockées sur la BDD MongoDB puis converties DataFrame')
                st.write(data_stream)

                # Display candlestick chart
                st.markdown('### Graphique en chandeliers 📈')
                #st.line_chart(data_stream,x="date", y="close")
                fig = create_candlestick_chart_MongoDB(data_stream)
                st.plotly_chart(fig, use_container_width=True)
                time.sleep(61)


with tab22:
    # Gérer l'état de l'authentification
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    with st.sidebar:
        st.title("Authentification")
        username = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe", type="password")
        auth_button = st.button("Valider l'authentification", key="auth_button")

    if auth_button:
        response = requests.get("http://api:8000/", auth=HTTPBasicAuth(username, password))
        if response.status_code == 200:
            st.session_state.authenticated = True
            st.success("Authentification réussie")
        else:
            st.session_state.authenticated = False
            st.sidebar.error("Authentification échouée")

    if st.session_state.authenticated:
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Accueil", "Entrainement ForecasterAutoreg", "Entrainement ARIMA", "Prédictions", "Mise à jour BDD", "Test requests de commandes curl"])
        
        with tab1:
            st.header("Accueil")
            st.write("Bienvenue sur le tableau de bord de prédiction des prix BTCEUR")

            curl_command1 = f"curl -u {username}:{password} -X 'GET' 'http://api:8000/' -H 'accept: application/json'"
            if st.button("Exécuter un test", key="test1_button"):
                output1 = subprocess.run(curl_command1, shell=True, capture_output=True, text=True)
                st.write("Résultat de la commande :")
                st.code(output1.stdout)

        with tab2:
            st.header("Entrainement du modèle ForecasterAutoreg")
            st.write("Infos: Permet de faire le re-entrainement du jeu de données")

            curl_command2 = f"curl -u {username}:{password} -X 'GET' 'http://api:8000/train/ForecasterAutoreg' -H 'accept: application/json'"
            if st.button("Exécuter un test", key="test2_button"):
                output2 = subprocess.run(curl_command2, shell=True, capture_output=True, text=True)
                st.write("Résultat de la commande :")
                st.code(output2.stdout)

        with tab3:
            st.header("Entrainement du modèle ARIMA")
            st.write("Infos: Permet de faire le re-entrainement du jeu de données")

            curl_command3 = f"curl -u {username}:{password} -X 'GET' 'http://api:8000/train/ARIMA' -H 'accept: application/json'"
            if st.button("Exécuter un test", key="test3_button"):
                output3 = subprocess.run(curl_command3, shell=True, capture_output=True, text=True)
                st.write("Résultat de la commande :")
                st.code(output3.stdout)

        with tab4:
            st.header("Prédictions des prix")
            st.write("Prédiction Des Prix")
            st.write("Sélectionnez l'un des modèles:")
            model_id = st.selectbox("Choisissez l'ID du Modèle", ["ForecasterAutoreg -> 1", "ARIMA -> 2"])
            close_time = st.text_input("Entrez la date de clôture (yyyy-mm-dd hh:00:00)", value=dt.now().strftime('%Y-%m-%d %H:00:00'))

            curl_command4 = f'''curl -u {username}:{password} -X 'POST' 'http://api:8000/BTCEUR/predict' \
                            -H 'accept: application/json' \
                            -H 'modelid: {model_id.split(" -> ")[1]}' \
                            -H 'Content-Type: application/json' \
                            -d '{{"close_time": "{close_time}"}}' '''
            if st.button("Exécuter un test", key="test4_button"):
                output4 = subprocess.run(curl_command4, shell=True, capture_output=True, text=True)
                st.write("Résultat de la commande :")
                st.code(output4.stdout)

        with tab5:
            st.header("Mise à jour de la base de données")
            st.write("Mise À Jour Des Données")
            st.write("Infos: Seul le compte admin est accepté pour la mise à jour")
            if st.button("Mettre à jour la base de données", key="update_db_button"):
                curl_command5 = f"curl -u {username}:{password} -X 'GET' 'http://api:8000/update/database' -H 'accept: application/json'"
                output5 = subprocess.run(curl_command5, shell=True, capture_output=True, text=True)
                st.write("Résultat de la commande :")
                st.code(output5.stdout)

        with tab6:
            st.title("Test de commandes curl")

            # Widget pour saisir les commandes curl
            curl_command = st.text_area("Entrez la commande curl", height=100)

            # Bouton pour exécuter la commande
            if st.button("Exécuter", key="curl_test_button"):
                curl_command = f"curl -u {username}:{password} " + curl_command
                output = subprocess.run(curl_command, shell=True, capture_output=True, text=True)
                # Affiche le résultat
                st.write("Résultat de la commande :")
                st.code(output.stdout)
    else:
        st.sidebar.error("Authentification échouée")