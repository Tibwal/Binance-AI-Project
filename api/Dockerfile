FROM python:3.11
#FROM ubuntu:18.04
#RUN apt-get update && apt-get install python3-pip -y
#RUN pip3 install --upgrade pip
COPY requirements.txt /my_work/requirements.txt
WORKDIR /my_work/
EXPOSE 8000
RUN pip3 install -r requirements.txt
ADD ["app.py", "table.py", "history_data.py", "train_model.py", "forAutoreg_model.sav", "ARIMA_model.sav", ".env", "/my_work"]
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
#CMD python3 app.py
