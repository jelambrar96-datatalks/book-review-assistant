#!/usr/bin/env bash

cd "$(dirname "$0")"

# docker compose build
docker compose build
docker compose --env-file .env up -d

sleep 5

CONTAINER_NAME="uploader" # taken from docker compose
docker wait $CONTAINER_NAME

# Get the container's exit code
EXIT_CODE=$(docker inspect $CONTAINER_NAME --format='{{.State.ExitCode}}')

# Check if the exit code is different from zero
if [ "$EXIT_CODE" -ne 0 ]; then
  echo "The container $CONTAINER_NAME finished with errors. Exit code: $EXIT_CODE"
  echo "Container logs:"
  docker logs $CONTAINER_NAME
else
    echo "The container $CONTAINER_NAME ran successfully."
fi

docker compose down
