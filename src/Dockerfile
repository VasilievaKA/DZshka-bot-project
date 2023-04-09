FROM python:3.10-buster
RUN pip install --upgrade pip
WORKDIR /src
COPY ./requirements.txt ./
RUN pip install -r requirements.txt
COPY . .
CMD python3 main.py