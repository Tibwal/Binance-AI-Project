import uvicorn
from fastapi import FastAPI,Depends, HTTPException, status,Header
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import pickle
import joblib
from typing import Optional
from skforecast.ForecasterAutoreg import ForecasterAutoreg
from pmdarima import ARIMA
from datetime import datetime as dt
import datetime
import json
import requests
import numpy as np
from pydantic import BaseModel
import pandas as pd
import binance
import pymysql
from sqlalchemy import create_engine
import mysql.connector
#import itertools
import os
from dotenv import load_dotenv
from table import crea_table, init_table_user
from history_data import Recup_data,injection_data
from train_model import train_forAutoreg,train_ARIMA


load_dotenv()

# récupération des variables d'environnement
host_opa=os.getenv('host')
user_opa=os.getenv('user')
password_opa=os.getenv('password')
database_opa=os.getenv('database')

class TypeData(BaseModel):
    """ format de la date:yyyy-mm-jj hh:00:00
    """
    close_time: dt
#from skforecast.ForecasterAutoreg import ForecasterAutoreg

app = FastAPI()


security = HTTPBasic()

# defining request url
url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCEUR"

#initialisation de la table utilisateur
init_table_user()
#connection à Mysql pour recuperer les infos utilisateurs
my_conn = create_engine("mysql+pymysql://{username}:{pw}@{hostname}/{db}".format(hostname=host_opa, db=database_opa, username=user_opa, pw=password_opa))


df_user =pd.read_sql('SELECT id, username,  password FROM utilisateur',con=my_conn)

def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    usernam = credentials.username
    passw = credentials.password

    if not (usernam in df_user.values) or not (passw in df_user.loc[df_user['username'] == usernam, 'password'].values):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    return credentials.username


def get_admin_user(credentials: HTTPBasicCredentials = Depends(security)):
    usernam = credentials.username
    passw = credentials.password

    if not (df_user.loc[df_user['username'] == os.getenv('ad'), 'username'].values == usernam) or not (passw in df_user.loc[df_user['username'] == os.getenv('ad'), 'password'].values):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    return credentials.username


#app init pour voir si l'api est fonctionnelle
@app.get('/')
def index():
    return {'message': ' prediction ML prix BTCEUR API'}


@app.post('/BTCEUR/predict',name='Prédiction des prix', tags =["modèles de machine learning"])
def predict_car_type(data:TypeData,modelid:Optional[int]= Header(None, description='Modele_ID'),username: str = Depends(get_current_user)):
    """ Selectionner l'un des modeles.

        **choisir l'id du Modèle:**
       
       - ForecasterAutoreg -> 1
       
       - ARIMA             -> 2
       
    """
    data = data.dict()
    print("la date de cloture sous format yyyy-mm-dd hh:00:00")
    close_time=data['close_time']

    # chargement des modeles
    loaded_model = pickle.load(open("forAutoreg_model.sav", 'rb'))
    loaded_model2 = pickle.load(open("ARIMA_model.sav", 'rb'))
    

    #prediction avec les 2 modeles 
    pred_price1 = loaded_model.predict(steps=5000)
    prediction1 = pred_price1.loc[close_time]
    pred_price2 = loaded_model2.predict(5000)
    prediction2 = pred_price2.loc[close_time]
    
    
    # requeter le prix actuel sur binance 
    Current_price = requests.get(url) 
    Current_price = Current_price.json()
    actual_price = Current_price['price']
    actual_price=float(actual_price)
    

    # json retourné par le modele selon le choix utilisateur
    if modelid == 1:
        return {
            'modèle': "AutoforcastReg",
            'prediction': prediction1,
            'Ecart entre la valeur actuelle et la valeur predite en %': 100*(prediction1 - actual_price)/actual_price
           }

    elif  modelid == 2:
        return {
            'modèle': "ARIMA",
            'prediction': prediction2,
            'Ecart entre la valeur actuelle et la valeur predite en %': 100*(prediction2 - actual_price)/actual_price
           }
    else:
        return {
            'marche à suivre': "vous devez selectionner 1 ou 2",
            
           }

@app.get('/update/database',name='Mise à jour des données', tags =["Base de données"])
def update_base(username: str = Depends(get_admin_user)):
    """ **Infos:** Seul le compte admin est accepté pour la mise à jour  """


    crea_table()
    injection_data()

    return {'Mysql': 'updated'}

@app.get('/train/ForecasterAutoreg',name='Entrainement des données', tags =["modèles de machine learning"])
def update_base(username: str = Depends(get_current_user)):
    """ **Infos:** Permet de faire le re-entrainement du jeux des données  """

    train_forAutoreg(my_conn)

    return {'ForecasterAutoreg train': 'OK'}


@app.get('/train/ARIMA',name='Entrainement des données', tags =["modèles de machine learning"])
def update_base(username: str = Depends(get_current_user)):
    """ **Infos:** Permet de faire le re-entrainement du jeux des données  """

    train_ARIMA(my_conn)

    return {'ARIMA train': 'OK'}

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)
