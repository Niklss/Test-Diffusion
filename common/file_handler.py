from io import StringIO, BytesIO
from pathlib import Path

import boto3
from botocore.config import Config
from botocore.errorfactory import BaseClientExceptions
from botocore.exceptions import EndpointConnectionError


class S3FileManager:
    """
    This class performs simple operations for working with S3
    """

    def __init__(self, endpoint_url, aws_access_key_id, aws_secret_access_key, bucket_name):
        """

        :param endpoint_url: Host url
        :param aws_access_key_id: Access key
        :param aws_secret_access_key: Secret key
        :param bucket_name: Bucket to work in
        """
        self.s3 = boto3.resource('s3', endpoint_url=endpoint_url, aws_access_key_id=aws_access_key_id,
                                 aws_secret_access_key=aws_secret_access_key, config=Config(signature_version='s3v4'),
                                 region_name='eu-west-1')
        self.bucket = self.s3.Bucket(bucket_name)
        self.bucket_name = bucket_name
        try:
            self.bucket.create()
        except BaseClientExceptions.ClientError:
            Exception('Wrong MinIO credentials')
        except EndpointConnectionError as e:
            raise e

    def save_file(self, file: BytesIO, path: Path, *args, **kwargs) -> None:
        """
        Upload object to S3
        :param file: File
        :param path: Path in S3 bucket with target name
        :param args:
        :param kwargs:
        :return:
        """
        self.bucket.put_object(Body=file, Key=path)

    def delete_file(self, path: Path, *args, **kwargs) -> None:
        """
        Delete file from S3
        :param path: Path to file in S3
        :param args:
        :param kwargs:
        :return:
        """
        self.bucket.delete_object(Key=path)

    def upload_file(self, source: Path, target: Path, *args, **kwargs) -> None:
        """
        Upload local file
        :param source: Path to local file
        :param target: Path in S3 bucket with target name
        :param args:
        :param kwargs:
        :return:
        """
        self.bucket.upload_file(Filename=source, Key=target)

    def load_file(self, path: Path, *args, **kwargs) -> StringIO:
        """
        Download a file as StringIO
        :param path: Path in S3 bucket
        :param args:
        :param kwargs:
        :return: Returns cursors to read from
        """
        return self.bucket.Object(path).get()['Body']

    def generate_access_link(self, path: Path, expiration=3600, *args, **kwargs) -> str:
        """
        Generate publically available link to object
        :param path: Path in S3 bucket
        :param expiration: Expiration time in seconds
        :param args:
        :param kwargs:
        :return:
        """
        return self.s3.meta.client.generate_presigned_url(ClientMethod='get_object',
                                                          Params={'Bucket': self.bucket_name, 'Key': path},
                                                          ExpiresIn=expiration)
