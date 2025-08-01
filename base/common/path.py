import boto3

COMMON_URL = 'http://192.168.31.14:7117'

REGION_NAME = 'Asia Pacific (Singapore) ap-southeast-1'
ACCESS_KEY = 'AKIAVOJTX26J5R6MV236'
SECRET_KEY = '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'
S3_BUCKET = 'businessapp-buck'

s3_client = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
                         aws_secret_access_key=SECRET_KEY)

def generate_presigned_url(file_name:str):
    """ generating s3 presigned url for files(object) """
    return s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET, 'Key': file_name},
            ExpiresIn=28800
        )