FROM ubuntu:18.04
RUN apt-get update && apt-get install python3-pip -y
COPY requirements.txt /my_work/requirements.txt
WORKDIR /my_work/
RUN pip3 install -r requirements.txt
ADD ["collect_streaming.py", ".env", "/my_work"]
#ADD collect_streaming.py /my_work/collect_streaming.py
CMD python3 collect_streaming.py
