FROM ubuntu:22.04

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update
RUN apt-get install -y curl python3.9 python3-pip

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

ENV OLLAMA_URI=$OLLAMA_URI
ENV OLLAMA_KEY=$OLLAMA_KEY
ENV OPENAI_API_KEY=$OPENAI_API_KEY
ENV OPENAI_MODEL=$OPENAI_MODEL
ENV ELASTICSEARCH_URI=$ELASTICSEARCH_URI
ENV ELASTICSEARCH_INDEX=$ELASTICSEARCH_INDEX

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]


