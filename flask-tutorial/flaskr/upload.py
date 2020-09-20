from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

import boto3
import os

S3_BUCKET = os.environ.get('S3_BUCKET')
S3_KEY = os.environ.get('S3_KEY')
S3_SECRET = os.environ.get('S3_SECRET_ACCESS_KEY')
# test
# S3_LOCATION = 'http://s3-video-test-1.s3.amazonaws.com/'
# prod
S3_LOCATION = 'http://lab-ken-video.com.s3.amazonaws.com/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov'])
# test
# S3_BUCKET_DIR = 'video-in/'
# prod
S3_BUCKET_DIR = 'media-original/'

s3 = boto3.client(
   "s3",
   aws_access_key_id = S3_KEY,
   aws_secret_access_key = S3_SECRET
)


def upload_file_to_s3(file, bucket_name, acl="public-read"):

    try:
        s3_bucket_path = os.path.join(S3_BUCKET_DIR, str(file.filename))
        s3.upload_fileobj(
            file,
            bucket_name,
            s3_bucket_path,
            ExtraArgs={
                "ACL": acl,
                "ContentType": file.content_type
            }
        )

    except Exception as e:
        print("Something Happened: ", e)
        return e

    return