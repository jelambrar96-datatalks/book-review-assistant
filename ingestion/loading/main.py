import os
import json
import hashlib

from io import BytesIO

from tqdm import tqdm

import pandas as pd
from minio import Minio

from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer

# Leer las variables de entorno
MINIO_URL = os.getenv('MINIO_URL')
ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
BUCKET_NAME = os.getenv('AWS_BUCKET_NAME')

URL_ELASTICSEARCH = os.getenv("URL_ELASTICSEARCH")
INDEX_NAME = os.getenv("INDEX_NAME", "default-index-name")

SAMPLE = os.getenv("SAMPLE")

model_name, dim_model = "all-mpnet-base-v2", 768
# model_name, dim_model = 'multi-qa-MiniLM-L6-cos-v1', 384
model = SentenceTransformer(model_name)

number_of_shards = 1
number_of_replicas = 0

INDEX_SETTINGS = {
    "settings": {
        "number_of_shards": number_of_shards,
        "number_of_replicas": number_of_replicas
    },
    "mappings": {
        "properties": {
            "title": {"type": "text"},
            "review_summary": {"type": "text"},
            "review_text": {"type": "text"},
            "description": {"type": "text"},
            "authors": {"type": "text"},
            "publisher": {"type": "text"},
            "categories": {"type": "text"},
            "review_score": {"type": "float"},
            "document_id": {"type": "keyword"},
            "document_data": {"type": "text"},
            "text_vector": {
                "type": "dense_vector",
                "dims": dim_model,
                "index": True,
                "similarity": "cosine"
            },
        }
    }
}


# Inicializar el cliente de MinIO
minio_client = Minio(
    MINIO_URL,
    access_key=ACCESS_KEY_ID,
    secret_key=SECRET_ACCESS_KEY,
    secure=False  # Cambia a True si el servidor usa HTTPS
)


# Función para descargar el archivo desde MinIO y cargarlo en un dataframe
def load_csv_from_minio(minio_client, bucket_name, file_name):
    # Descargar el archivo como stream de bytes
    response = minio_client.get_object(bucket_name, file_name)
    # Leer el archivo en un DataFrame de pandas
    csv_data = BytesIO(response.read())  # Convertir a BytesIO para que pandas pueda leerlo
    df = pd.read_csv(csv_data)
    # Cerrar el objeto de respuesta
    response.close()
    response.release_conn()
    return df


def generate_document_id(doc):
    combined = json.dumps(doc, sort_keys=True)
    hash_object = hashlib.md5(combined.encode(), usedforsecurity=False)
    hash_hex = hash_object.hexdigest()
    return hash_hex


def processing_dataset(
    df_book_data: pd.DataFrame,
    df_book_ratings: pd.DataFrame) -> pd.DataFrame:
    # remove unuseful columns from ratingd
    COLUMNS_DATASET = {
        "Title": "title",
        "review/score": "review_score",
        "review/summary": "review_summary",
        "review/text": "review_text"
    }
    COLUMN_LIST = list(COLUMNS_DATASET.keys())
    df_book_ratings = df_book_ratings[COLUMN_LIST]
    df_book_ratings = df_book_ratings.rename(columns=COLUMNS_DATASET)
    # remove unuseful columns from books data
    COLUMNS_DATASET = [
        "Title",
        "description",
        "authors",
        "publisher",
        "categories",
    ]
    df_book_data = df_book_data[COLUMNS_DATASET]
    df_book_data = df_book_data.rename(columns={"Title": "title"})
    # merge
    df_merged = pd.merge(left=df_book_ratings, right=df_book_data, on='title')
    df_merged = df_merged.fillna('')
    return df_merged


def load_dataset(df: pd.DataFrame):

    es_client = Elasticsearch(URL_ELASTICSEARCH)
    print(es_client.info())
    es_client.indices.delete(index=INDEX_NAME, ignore_unavailable=True)
    es_client.indices.create(index=INDEX_NAME, body=INDEX_SETTINGS)

    documents = df.to_dict(orient="records")
    # len_documents = len(documents)
    for document in tqdm(documents):
        document['document_id'] = generate_document_id(document)
        # print("loading document: ", document['document_id'][:8], f"{i+1} of {len_documents}")
        document_data = f"{document['title']}. {document['authors']}. " + document['review_summary']
        document['document_data'] = document_data
        document['text_vector'] = model.encode(document_data)
        es_client.index(index=INDEX_NAME, document=document)
    
    # es_client.close()

def main():
    # Nombres de los archivos CSV en el bucket
    csv_file_1 = 'raw_dataset/amazon-books-reviews/ratings.csv'
    csv_file_2 = 'raw_dataset/amazon-books-reviews/data.csv'

    # Cargar los dos archivos en dataframes
    print("loading file ", os.path.basename(csv_file_1), "from minio")
    df1 = load_csv_from_minio(minio_client, BUCKET_NAME, csv_file_1)
    print("loading file ", os.path.basename(csv_file_2), "from minio")
    df2 = load_csv_from_minio(minio_client, BUCKET_NAME, csv_file_2)

    # Mostrar los DataFrames cargados (o manejar de acuerdo a tus necesidades)
    # print(f"DataFrame 1: {df1.head()}")
    # print(f"DataFrame 2: {df2.head()}")
    print("creating output dataframe")
    df = processing_dataset(df2, df1)
    del df1
    del df2
    print("loading dataset")
    if SAMPLE is not None:
        nsample = int(SAMPLE)
        df = df.sample(nsample, random_state=1)
    load_dataset(df)


main()