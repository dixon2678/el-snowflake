FROM python:3.8.2
WORKDIR /
RUN apt-get update
RUN apt-get install default-jdk -y

COPY ./requirements.txt /requirements.txt
RUN pip install -r requirements.txt

COPY . /

ENTRYPOINT [ "python" ]

CMD ["./source/main.py"]