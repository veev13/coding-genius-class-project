FROM python:3.7.9-stretch

WORKDIR /mydata
RUN pip install requests
RUN pip install beautifulsoup4
RUN pip install kafka-python
RUN pip install jsons
RUN pip install pymysql
RUN pip install python-consul
RUN pip install threaded

COPY ./test_single1.py ./stockparser.py
CMD ["python", "stockparser.py"]

