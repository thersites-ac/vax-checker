FROM ubuntu

RUN apt-get update
RUN apt-get install -y python3-pip

RUN pip3 install requests
RUN pip3 install boto3

COPY query_vax.py .

ENTRYPOINT python3 query_vax.py 1
