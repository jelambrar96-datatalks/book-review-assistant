FROM ubuntu:22.04

ARG DEBIAN_FRONTEND=noninteractive

ENV KAGGLE_USERNAME=$KAGGLE_USERNAME
ENV KAGGLE_KEY=$KAGGLE_KEY

ENV AWS_BUCKET_NAME=$AWS_BUCKET_NAME
ENV AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
ENV AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY

ENV MINIO_ENDPOINT=$AWS_URI
ENV MINIO_ALIAS=$MINIO_ALIAS

ENV UNZIP_DATASET=$UNZIP_DATASET

RUN apt-get update
RUN apt-get install -y python3 python3-pip awscli curl unzip \
    wget ca-certificates
RUN pip install --no-cache-dir kaggle

RUN wget https://dl.min.io/client/mc/release/linux-amd64/mc && \
    chmod +x mc && \
    mv mc /usr/local/bin/mc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN useradd -ms /bin/bash kaggle
USER kaggle
WORKDIR /home/kaggle

COPY run.sh .

CMD ["bash", "run.sh"]
