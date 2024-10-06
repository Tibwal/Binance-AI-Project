import os
import pickle
from skforecast.ForecasterAutoreg import ForecasterAutoreg
from pmdarima import ARIMA
from lightgbm import LGBMRegressor
import pandas as pd

def train_forAutoreg(mon_conn):
  if os.path.exists("forAutoreg_model.sav"):
    os.remove("forAutoreg_model.sav")
  

  # selection des données dans la base 
  df =pd.read_sql('SELECT close_time, close FROM history_Data WHERE symbol_id =1 AND  granularity_id =1',con=mon_conn)

  # Mise en forme
  df = df.set_index('close_time')
  df = df.asfreq(freq='H', method='bfill')
  df = df.sort_index()

  #Entrainement
  lag = 389
  #instanciation
  forecaster = ForecasterAutoreg(
                     regressor     = LGBMRegressor(random_state=213),
                     lags          = lag,
                     transformer_y = None
                 )

  forecaster.fit(y=df['close'])

  # enregistrer le model sur le disk
  filename = 'forAutoreg_model.sav'
  pickle.dump(forecaster, open(filename, 'wb'))


def train_ARIMA(mon_conn):
  if os.path.exists("ARIMA_model.sav"):
    os.remove("ARIMA_model.sav")

  # selection des données dans la base 
  df =pd.read_sql('SELECT close_time, close FROM history_Data WHERE symbol_id =1 AND  granularity_id =1',con=mon_conn)

  #Mise en forme
  df = df.set_index('close_time')
  df = df.asfreq(freq='H', method='bfill')
  df = df.sort_index()

  #Entrainement
  model_arima = ARIMA(order = (2,1,2))
  model_arima_fit = model_arima.fit(y=df)

  # enregistrer le model sur le disk
  filename = 'ARIMA_model.sav'
  pickle.dump(model_arima_fit, open(filename, 'wb'))
