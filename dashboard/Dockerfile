FROM python:3.11
#FROM ubuntu:18.04
#RUN apt-get update && apt-get install python3-pip -y
RUN apt-get update
RUN apt-get install python3-dev default-libmysqlclient-dev build-essential pkg-config -y
COPY requirements.txt /my_work/requirements.txt
WORKDIR /my_work/
RUN pip3 install -r requirements.txt
ADD ["HistoStreamDataDashboard_sql.py", "/my_work"]
COPY .streamlit/ /my_work/.streamlit/
CMD streamlit run HistoStreamDataDashboard_sql.py --server.port=8501

