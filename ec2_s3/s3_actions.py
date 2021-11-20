import os, boto3, botocore, ec2_s3


class S3Actions:
    def __init__(self, log_file_name=''):
        self.s3_client = boto3.client('s3')
        self.my_log = ec2_s3.LogActions(log_file_name)

    def create_s3_bucket(self, bucket_name):
        try:
            self.s3_client.create_bucket(ACL='private', Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': 'us-west-2'})
        except botocore.exceptions.ClientError as e:
            print(e)
            self.my_log.log_user_actions('error', e)

    def upload_object(self, bucket_name, file_path):
        try:
            file_name = os.path.split(file_path)[1]
            self.s3_client.upload_file(file_path, bucket_name, file_name)
        except FileNotFoundError as e:
            print(e)
            self.my_log.log_user_actions('error', e)
        except boto3.exceptions.S3UploadFailedError as e:
            print("{}. (Passed bucket name may be wrong, please double check)".format(e))
            self.my_log.log_user_actions('error', e)

    def list_buckets(self):
        my_buckets = self.s3_client.list_buckets()['Buckets']
        buckets = []
        for every_bucket in my_buckets:
            buckets.append(every_bucket)
        return buckets

    def delete_objects(self, bucket_name, object_name):
        try:
            self.s3_client.delete_object(
                Bucket=bucket_name,
                Key=object_name)
        except self.s3_client.exceptions.ClientError as e:
            print(e)
            self.my_log.log_user_actions('error', e)

    def delete_bucket(self, bucket_name):
        try:
            self.s3_client.delete_bucket(Bucket=bucket_name)
        except self.s3_client.exceptions.ClientError as e:
            print(e)
            self.my_log.log_user_actions('error', e)

    def download_object(self, bucket_name, object_name, destination_folder):
        try:
            destination_path = os.path.join(destination_folder, object_name)
            print(destination_path)
            self.s3_client.download_file(bucket_name, object_name, destination_path)
        except self.s3_client.exceptions.ClientError as e:
            print(e)
            self.my_log.log_user_actions('error', e)

    def list_objects(self, bucket_name):
        try:
            my_objects = self.s3_client.list_objects(Bucket=bucket_name)
        except self.s3_client.exceptions.NoSuchBucket as e:
            print(e)
            self.my_log.log_user_actions('error', e)
        except botocore.exceptions.ClientError as e:
            print(e)
            self.my_log.log_user_actions('error', e)
        else:
            if "Contents" in my_objects:
                for obj in my_objects['Contents']:
                    print('{} | Size: {} KB | Last Modified: {}'.format(obj['Key'], obj['Size'], obj['LastModified']))