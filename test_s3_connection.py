import boto3
import os
from dotenv import load_dotenv
load_dotenv()

s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION")
)

s3.put_object(
    Bucket="finnhub-pipeline-288831154476-us-east-1-an",
    Key="bronze/test/connection_test.txt",
    Body=b"connection successful"
)
print("✅ S3 write successful — pipeline is ready")

s3.delete_object(
    Bucket="finnhub-pipeline-288831154476-us-east-1-an",
    Key="bronze/test/connection_test.txt"
)
print("✅ S3 delete successful")
print("✅ S3 fully configured — ready to build pipeline subclasses")