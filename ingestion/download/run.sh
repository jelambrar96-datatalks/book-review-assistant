#!/bin/bash

DATASET_NAME=amazon-books-reviews
DATASET_FILE=$DATASET_NAME.zip
CSV_FILE_1="./Books_rating.csv"
CSV_FILE_2="./books_data.csv"

MINIO_SERVER="$AWS_URI"
BUCKET_NAME="$AWS_BUCKET_NAME"
ACCESS_KEY="$AWS_ACCESS_KEY_ID"
SECRET_KEY="$AWS_SECRET_ACCESS_KEY"

UNZIP_FILE="$UNZIP_DATASET"

# Create bucket
# create_bucket "$BUCKET_NAME"
mc alias set $MINIO_ALIAS $MINIO_SERVER $ACCESS_KEY $SECRET_KEY
mc mb $MINIO_ALIAS/$BUCKET_NAME --ignore-existing

# download files
KAGGLE_DIR='/home/kaggle/.kaggle'
mkdir -p $KAGGLE_DIR
echo '{"username": "${KAGGLE_USERNAME}", "key": "${KAGGLE_KEY}"}' >> $KAGGLE_DIR/.kaggle.json
kaggle datasets download -d mohamedbakhet/amazon-books-reviews --force

# send files to minio
mc cp $DATASET_NAME.zip $MINIO_ALIAS/$BUCKET_NAME/raw_dataset/$DATASET_NAME.zip

if [[ "$UNZIP_FILE" == "true" ]]; then
    unzip -o amazon-books-reviews.zip
    mc cp $CSV_FILE_1 $MINIO_ALIAS/$BUCKET_NAME/raw_dataset/$DATASET_NAME/ratings.csv
    mc cp $CSV_FILE_2 $MINIO_ALIAS/$BUCKET_NAME/raw_dataset/$DATASET_NAME/data.csv
fi
