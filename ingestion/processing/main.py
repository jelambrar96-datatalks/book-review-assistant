import os
import json
import re
import zipfile

from io import BytesIO
from typing import Dict

import pandas as pd
import pyarrow
import s3fs

from minio import Minio


# Leer las variables de entorno
MINIO_URL = os.getenv('MINIO_URL')
ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
BUCKET_NAME = os.getenv('AWS_BUCKET_NAME')

# Inicializar el cliente de MinIO
minio_client = Minio(
    MINIO_URL,
    access_key=ACCESS_KEY_ID,
    secret_key=SECRET_ACCESS_KEY,
    secure=False  # Cambia a True si el servidor usa HTTPS
)

fs = s3fs.S3FileSystem(
    anon=False,
    key=ACCESS_KEY_ID,
    secret=SECRET_ACCESS_KEY,
    client_kwargs={'endpoint_url': f"http://{MINIO_URL}"}
)


def load_dataset_from_zip_minio(
        minio_client: str,
        bucket_name: str,
        file_name: str
    ) -> Dict:
    # Descargar el archivo como stream de bytes
    output = {}
    response = minio_client.get_object(bucket_name, file_name)
    zip_buffer = BytesIO(response.read())
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zfile:
        with zfile.open('books_data.csv') as books_data_file:
            df_books_data = pd.read_csv(books_data_file)
            output['books_data.csv'] = df_books_data
        with zfile.open('Books_rating.csv') as books_rating_file:
            df_books_rating = pd.read_csv(books_rating_file)
            output['Books_rating.csv'] = df_books_rating
    return output


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


def to_snake_case(name):

    def replace_non_alphanumeric_and_reduce_spaces(text):
        # Replace non-alphanumeric characters with spaces
        text = re.sub(r'[^a-zA-Z0-9]', ' ', text)
        # Remove multiple spaces by replacing them with a single space
        text = re.sub(r'\s+', ' ', text)
        # Strip leading/trailing spaces
        return text.strip()

    name = replace_non_alphanumeric_and_reduce_spaces(name)
    name = re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()
    name = name.replace(' ', '_')
    return name


def convert_columns_df(df: pd.DataFrame) -> pd.DataFrame:
    df_columns = list(df.columns)
    dict_rename = dict((item, to_snake_case(item)) for item in df_columns)
    df = df.rename(columns=dict_rename)
    return df


def main():
    # Nombres de los archivos ZIP
    zip_filepath = 'raw_dataset/amazon-books-reviews.zip'
    # Cargar los dos archivos en dataframes
    print("loading dataframes from minio...")
    dataframes_dict = load_dataset_from_zip_minio(
        minio_client=minio_client,
        bucket_name=BUCKET_NAME,
        file_name=zip_filepath)
    # rename columns dataframe
    print("renaming columns from datasets...")
    for k in dataframes_dict.keys():
        dataframes_dict[k] = convert_columns_df(dataframes_dict[k])
    # merged dataframes
    print("mergins datasets...")
    df_merged = pd.merge(
        left=dataframes_dict['Books_rating.csv'],
        right=dataframes_dict['books_data.csv'],
        on='title', how='inner')
    print("creatins datetime columns....")
    df_merged['review_datetime'] = pd.to_datetime(df_merged['review_time'], unit='s')
    # df_merged['year'] = pd.DatetimeIndex(df['review_datetime']).year
    # df_merged['month'] = pd.DatetimeIndex(df['review_datetime']).month
    # df_merged['day'] = pd.DatetimeIndex(df['review_datetime']).day
    df_merged['year'] = df_merged['review_datetime'].dt.year
    df_merged['month'] = df_merged['review_datetime'].dt.month
    # df_merged['day'] = df_merged['review_datetime'].dt.day
    # Guardar el DataFrame particionado por año, mes, día en formato Parquet
    print("sending to minio....")
    df_merged.to_parquet(
        f's3://{BUCKET_NAME}/datasets/amazon-books-reviews/',
        filesystem=fs,
        partition_cols=['year', 'month'],
        engine='pyarrow'
    )
    print("success")


if __name__ == '__main__':
    main()