import pandas as pd
import binance
import datetime
import pymysql
import mysql.connector
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv


# definition de la fonction de collecte
def Recup_data(client,symbol,id_symbol,id_granularity,decalage):
    date='2020-01-01'
    start_date = datetime.datetime.strptime(date, '%Y-%m-%d')
    #delta = 1000*60*60

    timestamp=int(datetime.datetime.timestamp(pd.to_datetime(start_date))*1000) # Conversion en timestamp

    if id_granularity == 1:
        klines = client.get_historical_klines(symbol, client.KLINE_INTERVAL_1HOUR,timestamp)

    else:
        klines = client.get_historical_klines(symbol, client.KLINE_INTERVAL_1DAY,timestamp,limit=1000 )

    data = pd.DataFrame(data = [row[1:7] for row in klines], columns = ['open', 'high', 'low', 'close', 'volume','close_time'])

    data['close_time'] = pd.to_datetime(data['close_time'] + decalage, unit='ms')
    data.loc[:, data.columns != 'close_time'] = data.loc[:, data.columns != 'close_time'].astype(float)

    data['symbol_id'] = id_symbol
    data['granularity_id'] = id_granularity
    df=data.reindex(columns=['close_time','symbol_id','granularity_id','open', 'high', 'low', 'close', 'volume'])

    return df


def injection_data():
    # Load environment variables from .env file
    load_dotenv()

    myclient = binance.Client()
    df_1h_BTCEUR=Recup_data(myclient,"BTCEUR",1,1,1000*60*60)
    df_1h_ETHEUR=Recup_data(myclient,"ETHEUR",2,1,1000*60*60)
    df_1d_BTCEUR=Recup_data(myclient,"BTCEUR",1,2,0)
    df_1d_ETHEUR=Recup_data(myclient,"ETHEUR",2,2,0)

    # concatenation des df
    train_df_list = [df_1h_BTCEUR,df_1h_ETHEUR, df_1d_BTCEUR,df_1d_ETHEUR]
    train_df = pd.concat(train_df_list, ignore_index=True)

    # récupération des variables d'environnement
    host_opa=os.getenv('host')
    user_opa=os.getenv('user')
    password_opa=os.getenv('password')
    database_opa=os.getenv('database')

    #Insertion des données dans la base
    my_conn = create_engine("mysql+pymysql://{username}:{pw}@{hostname}/{db}".format(hostname=host_opa, db=database_opa, username=user_opa, pw=password_opa))
    train_df.to_sql('history_Data', my_conn, if_exists = 'append', index=False)
