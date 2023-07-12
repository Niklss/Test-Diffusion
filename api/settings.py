import os

from producer import AIOProducer
from common import S3FileManager

MINIO_ENDPOINT_URL = os.getenv('MINIO_ENDPOINT_URL')
MINIO_ACCESS_KEY_ID = os.getenv('MINIO_ACCESS_KEY_ID')
MINIO_SECRET_ACCESS_KEY = os.getenv('MINIO_SECRET_ACCESS_KEY')
MINIO_IMAGE_BUCKET_NAME = os.getenv('MINIO_IMAGE_BUCKET_NAME')
file_manager = S3FileManager(MINIO_ENDPOINT_URL, MINIO_ACCESS_KEY_ID, MINIO_SECRET_ACCESS_KEY,
                             MINIO_IMAGE_BUCKET_NAME)

KAFKA_PRODUCER_CONFIG = eval(os.getenv('KAFKA_PRODUCER_CONFIG'))
producer = AIOProducer(KAFKA_PRODUCER_CONFIG)

with open(os.getenv('MODEL_NAMES_PATH'), 'r') as file:
    model_names = file.read().split('\n')
