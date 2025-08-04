import boto3,os
from dotenv import load_dotenv
from pathlib import Path
load_dotenv()

# env_path = Path('/var/www/html/backend/base/.env')
# load_dotenv(dotenv_path=env_path)

COMMON_URL = 'http://192.168.31.14:7117'

REGION_NAME = os.getenv("REGION_NAME")
ACCESS_KEY = os.getenv("ACCESS_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")
S3_BUCKET = os.getenv("S3_BUCKET")

s3_client = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
                         aws_secret_access_key=SECRET_KEY)

def generate_presigned_url(file_name:str):
    """ generating s3 presigned url for files(object) """
    return s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET, 'Key': file_name},
            ExpiresIn=28800
        )