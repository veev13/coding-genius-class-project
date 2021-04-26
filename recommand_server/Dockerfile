FROM python:3.7.9-stretch

WORKDIR /mydata
RUN pip install requests
RUN pip install jsons
RUN pip install pymysql
RUN pip install python-consul
RUN pip install threaded

COPY ./recommand.py ./recommand.py
CMD ["python", "recommand.py"]

