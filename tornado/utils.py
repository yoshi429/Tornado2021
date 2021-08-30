import boto3
import os
import secrets
from PIL import Image
from flask import current_app
from tornado import app
from tornado.models import post_goods


# ローカルに写真を保存
def save_picture(picture, picture_save_path, user_id):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(picture.filename)
    picture_fn = random_hex + user_id + f_ext
    picture_path = os.path.join(current_app.root_path, picture_save_path, picture_fn)
    print(picture_fn)
    print(picture_path)
    i = Image.open(picture)
    i.save(picture_path)
    
    return picture_fn


# amazon s3 で保存
def save_pictures_s3(picture, user_id):
    aws_access_key_id = app.config["AWS_ACCESS_KEY_ID"]
    aws_secret_access_key = app.config["AWS_SECRET_ACCESS_KEY"]
    s3_bucket = app.config['S3_BUCKET']

    s3 = boto3.client('s3',
                region_name='us-east-1',
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                )
                
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(picture.filename)
    picture_fn = random_hex + str(user_id) + f_ext
    response = s3.put_object(
            Body=picture,
            Bucket=s3_bucket,
            Key=picture_fn
        )
    return f"https://tornado2021.s3.amazonaws.com/{picture_fn}"


def get_public_url(bucket, target_object_path, s3):
    """
    対象のS3ファイルのURLを取得する

    Parameters
    ----------
    bucket: string
        S3のバケット名
    target_object_path: string
        取得したいS3内のファイルパス

    Returns
    ----------
    url: string
        S3上のオブジェクトのURL
    """
    bucket_location = s3.get_bucket_location(Bucket=bucket)
    return "https://s3-{0}.amazonaws.com/{1}/{2}".format(
        bucket_location['LocationConstraint'],
        bucket,
        target_object_path)
