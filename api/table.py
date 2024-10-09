import mysql.connector
import os
from dotenv import load_dotenv


def crea_table():
    
    # Load environment variables from .env file
    load_dotenv()

    db = mysql.connector.connect(
        host=os.getenv('host'),
        user=os.getenv('user'),
        password=os.getenv('password'),
        database=os.getenv('database')
    )

    mycursor = db.cursor()

    #suppression des tables existantes
    mycursor.execute("DROP TABLE IF EXISTS history_Data")
    mycursor.execute("DROP TABLE IF EXISTS symbol")
    mycursor.execute("DROP TABLE IF EXISTS granularity")
    mycursor.execute("DROP TABLE IF EXISTS utilisateur")

    # Creation des tables
    mycursor.execute("CREATE TABLE symbol (id INTEGER NOT NULL, symbol VARCHAR(255),PRIMARY KEY (id))")
    mycursor.execute("CREATE TABLE granularity (id INTEGER NOT NULL, granularity VARCHAR(255),PRIMARY KEY (id))")
    mycursor.execute("CREATE TABLE utilisateur (id INTEGER NOT NULL, username VARCHAR(255),password VARCHAR(255))")

    # Insertion des valeurs
    sql = "INSERT INTO symbol (id, symbol) VALUES (%s, %s)"
    val = [
    (1, 'BTCEUR'),
    (2, 'ETHEUR')
    ]

    mycursor.executemany(sql,val)
    db.commit()

    sql = "INSERT INTO granularity (id, granularity) VALUES (%s, %s)"
    val = [
    (1, '1_HOUR'),
    (2, '1_DAY')
    ]

    mycursor.executemany(sql,val)
    db.commit()

    sql = "INSERT INTO utilisateur (id, username, password) VALUES (%s, %s, %s)"
    val = [
    (1, os.getenv('user'), os.getenv('password')),
    (1, os.getenv('ad'),os.getenv('adpass'))
    ]

    mycursor.executemany(sql,val)
    db.commit()

    # creation de la table history_Data
    mycursor.execute("CREATE TABLE history_Data (id INTEGER NOT NULL AUTO_INCREMENT, close_time DATETIME,symbol_id INTEGER,granularity_id INTEGER,open FLOAT,high FLOAT,low FLOAT,close FLOAT,volume FLOAT, PRIMARY KEY (id),FOREIGN KEY(symbol_id) REFERENCES symbol (id),FOREIGN KEY(granularity_id) REFERENCES granularity (id))")

    db.commit()

    db.close()



def init_table_user():

    # Load environment variables from .env file
    load_dotenv()

    db = mysql.connector.connect(
        host=os.getenv('host'),
        user=os.getenv('user'),
        password=os.getenv('password'),
        database=os.getenv('database')
    )

    mycursor = db.cursor()

    mycursor.execute("DROP TABLE IF EXISTS utilisateur")

    mycursor.execute("CREATE TABLE utilisateur (id INTEGER NOT NULL, username VARCHAR(255),password VARCHAR(255))")

    sql = "INSERT INTO utilisateur (id, username, password) VALUES (%s, %s, %s)"
    val = [
    (1, os.getenv('user'), os.getenv('password')),
    (1, os.getenv('ad'),os.getenv('adpass'))
    ]

    mycursor.executemany(sql,val)
    db.commit()

    db.close()

