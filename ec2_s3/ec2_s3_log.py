import logging, os, ec2_s3


class LogActions:
    def __init__(self, log_file_name=''):
        if len(log_file_name) > 0:
            self.log_file = os.path.join(os.getcwd(), log_file_name)
        else:
            self.log_file = os.path.join(os.getcwd(), 'ec2_s3_logs.txt')

    def creat_log_file(self):
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w') as f:
                pass

    def upload_log_s3(self, bucket_name):
        my_s3 = ec2_s3.S3Actions()
        my_bucket_names = []
        for bucket in my_s3.list_buckets():
            my_bucket_names.append(bucket['Name'])
            # creates a log bucket if it doesn't exist
        if bucket_name not in my_bucket_names:
            my_s3.create_s3_bucket(bucket_name)
        my_s3.upload_object(bucket_name, self.log_file)

    def log_user_actions(self, log_level, report, user=''):
        self.creat_log_file()
        logging.basicConfig(filename=self.log_file, level=logging.INFO,
                            format='%(levelname)s:%(asctime)s - %(message)s')
        if log_level.lower() == 'info':
            logging.info(f'{user}:{report}')
        if log_level.lower() == 'error':
            logging.error(f'{user}:{report}')
        if log_level.lower() == 'warning':
            logging.warning(f'{user}:{report}')
