import argparse
from pprint import pprint
from sys import path
import openpyxl as xl
import os
import logging
import boto3
import botocore


def instances(list_of_instances):
    my_instances = []
    my_instance_ids = []
    for item in list_of_instances['Reservations']:
        for each_instance in item['Instances']:
            my_instances.append(each_instance)
            my_instance_ids.append(each_instance['InstanceId'])
    return [my_instances, my_instance_ids]


def list_instances(instance_id):
    ec2_client = boto3.client('ec2')
    if instance_id:
        try:
            list_instances = ec2_client.describe_instances(Filters=[{'Name': 'instance-id', 'Values': [instance_id]}])
            pprint(list_instances['Reservations'][0]['Instances'])
        except IndexError:
            print("Invalid instance ID was passed")
    else:
        list_instances = ec2_client.describe_instances()
        count = 0
        for each_instance in instances(list_instances)[0]:
            count += 1
            print("{} Instance ID: {} | Instance Type: {} | Instance State: {}".format(count, each_instance['InstanceId'], each_instance['InstanceType'], each_instance['State']['Name']))


def create_instances(num_of_instances, image_id, instance_type):
    ec2_resource = boto3.resource('ec2')
    ec2_client = boto3.client('ec2')
    keypair_name = ec2_client.describe_key_pairs()['KeyPairs'][0]['KeyName']
    ec2_resource.create_instances(ImageId=image_id, InstanceType=instance_type, KeyName=keypair_name,
                                  MaxCount=num_of_instances, MinCount=1)


def change_instance_state(instance_id, instance_state):
    ec2_client = boto3.client('ec2')
    try:
        if instance_state == 'run':
            ec2_client.start_instances(InstanceIds=instance_id)
            print("starting instances...")
            ec2_client.get_waiter('instance_running').wait(InstanceIds=instance_id)
            print("Instance(s) are up and running")
        elif instance_state == 'stop':
            ec2_client.stop_instances(InstanceIds=instance_id)
            print("stopping instances...")
            ec2_client.get_waiter('instance_stopped').wait(InstanceIds=instance_id)
            print("Instance(s) stopped")
        elif instance_state == 'terminate':
            ec2_client.terminate_instances(InstanceIds=instance_id)
            print("terminating instances...")
            ec2_client.get_waiter('instance_terminated').wait(InstanceIds=instance_id)
            print("Instance(s)s terminated")
    except botocore.exceptions.ClientError as e:
        print(e)


def create_instance_from_excel_sheet(excel_file_path):
    try:
        excel_file = xl.load_workbook(excel_file_path)
        sheet = excel_file['Sheet1']
        instance_type = sheet['b1'].value
        ami_id = sheet['b2'].value
        keypair = sheet['b3'].value
        num_of_instances = sheet['b4'].value
        sg_id = sheet['b5'].value
        subnet_id = sheet['b6'].value
        ec2_resource = boto3.resource('ec2')
        ec2_resource.create_instances(ImageId=ami_id, InstanceType=instance_type, SecurityGroupIds=[sg_id], SubnetId=subnet_id, KeyName=keypair, MaxCount=num_of_instances, MinCount=1)
    except xl.utils.exceptions.InvalidFileException as e:
        print(e)
    except botocore.exceptions.ParamValidationError as e:
        print(e)
    except botocore.exceptions.ClientError as e:
        print(e)


def create_s3_bucket(bucket_name):
    try:
        s3_client = boto3.client('s3')
        s3_client.create_bucket(
            ACL='private', Bucket=bucket_name,
            CreateBucketConfiguration={'LocationConstraint': 'us-west-2'})
    except boto3.exceptions as e:
        print(e)


def upload_object(bucket_name, file_path):
    try:
        file_name = os.path.split(file_path)[1]
        s3_client = boto3.client('s3')
        s3_client.upload_file(file_path, bucket_name, file_name)
    except FileNotFoundError as e:
        print(e)
    except boto3.exceptions.S3UploadFailedError as e:
        print(e)


def list_buckets():
    s3_client = boto3.client('s3')
    my_buckets = s3_client.list_buckets()['Buckets']
    buckets = []
    for every_bucket in my_buckets:
        buckets.append(every_bucket)
    return buckets


def delete_objects(bucket_name, object_name):
    try:
        s3_client = boto3.client('s3')
        s3_client.delete_object(
            Bucket=bucket_name,
            Key=object_name)
    except boto3.exceptions as e:
        print(e)


def delete_bucket(bucket_name):
    try:
        s3_client = boto3.client('s3')
        s3_client.delete_bucket(Bucket=bucket_name)
    except boto3.exceptions as e:
        print(e)


def download_object(bucket_name, object_name, destination_folder):
    try:
        s3_client = boto3.client('s3')
        destination_path = os.path.join(destination_folder, object_name)
        print(destination_path)
        s3_client.download_file(bucket_name, object_name, destination_path)
    except boto3.exceptions as e:
        print(e)


def list_objects(bucket_name):
    try:
        s3_client = boto3.client('s3')
        my_objects = s3_client.list_objects(Bucket=bucket_name)
        return my_objects['Contents']
    except boto3.exceptions as e:
        print(e)


def log_user_actions(action, log_file_path):
    my_bucket_names = []
    for bucket in list_buckets():
        my_bucket_names.append(bucket['Name'])
    if 'ec2-s3-awsconsoleboto3' not in my_bucket_names:
        create_s3_bucket('ec2-s3-awsconsoleboto3')
    logging.info(action)
    upload_object('ec2-s3-awsconsoleboto3-logs', log_file_path)


if __name__ == "__main__":

    log_file = os.path.join(os.environ.get('HOME'), 'user_actions_log.txt')
    if not os.path.exists(log_file):
        with open(log_file, 'w') as f:
            pass

    logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

    ec2_client = boto3.client('ec2')
    amazon_linux_free_tier_ami = ec2_client.describe_images(
        Filters=[{'Name': 'description', 'Values': ['Amazon Linux 2 AMI 2.0.20210318.0 x86_64 HVM gp2']}])['Images']
    image_id = amazon_linux_free_tier_ami[0]['ImageId']

    parser = argparse.ArgumentParser(
        formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=30, width=1000, indent_increment=5),
        description="Interact with EC2 and S3")
    ec2_group = parser.add_argument_group('EC2 arguments')
    s3_group = parser.add_argument_group('S3 arguments')

    ec2_group.add_argument("-c", "--create", help="Launch instance, pass the number of instances to launch or excel file, optionally pass desired AMI ID", metavar='')
    ec2_group.add_argument("-l", "--list", action="store_true", help="List instances, optionally pass instance ID to get more information on a specific instance")
    ec2_group.add_argument("--type", help="Pass instance type", metavar='', default='t2.micro')
    ec2_group.add_argument("--ami", help="Pass AMI ID", metavar='', default=image_id)
    ec2_group.add_argument("-s", "--state", help="Change state of all instances unless instance ID is passed, pass state to chage to (stop, start, or terminate)", choices=['terminate', 'stop', 'run'], metavar='')
    ec2_group.add_argument("-id", help="Pass instance ID or AMI ID", metavar='')
    s3_group.add_argument('-cb', help="Create bucket, pass bucket name", metavar='B')
    s3_group.add_argument('-lb', help="List buckets", action="store_true")
    s3_group.add_argument('-lo', help="List objects/files in a particular bucket, must pass bucket name", metavar='')
    s3_group.add_argument("--upload", nargs='+', help="Upload file to specified bucket, pass bucket name and file path", metavar='')
    s3_group.add_argument("--download", nargs='+', help="Download object from a bucket, pass bucket name, object name, and destination folder", metavar='')
    s3_group.add_argument('--delobj', nargs='+', help="Delete object, pass bucket name and object name",  metavar='')
    s3_group.add_argument('--delbkt', help="Delete bucket, must pass bucket name", metavar='')
    args = parser.parse_args()

    if args.list:
        list_instances(args.id)
        log_user_actions('list instance', log_file)
    elif args.create:
        if args.create.isdigit():
            create_instances(int(args.create), args.ami, args.type)
        else:
            create_instance_from_excel_sheet(args.create)
        log_user_actions('launch instance', log_file)
    elif args.state:
        if args.id:
            change_instance_state([args.id], args.state)
        else:
            ec2_client = boto3.client('ec2')
            instance_state_filter = [
                {'Name': 'instance-state-name', 'Values': ['pending', 'stopped', 'running', 'stopping']}]
            list_instances = ec2_client.describe_instances(Filters=instance_state_filter)
            my_instance_ids = instances(list_instances)[1]
            change_instance_state(my_instance_ids, args.state)
        log_user_actions('change instance state', log_file)
    elif args.cb:
        create_s3_bucket(args.cb)
        log_user_actions('create s3 bucket', log_file)
    elif args.lb:
        for bucket in list_buckets():
            print('Bucket Name: {} | Date Created: {}'.format(bucket['Name'], bucket['CreationDate']))
        log_user_actions('list bucket', log_file)
    elif args.lo:
        objs = list_objects(args.lo)
        for obj in objs:
            print('{} | Size: {} KB | Last Modified: {}'.format(obj['Key'], obj['Size'], obj['LastModified']))
        log_user_actions('list object', log_file)
    elif args.upload:
        upload_object(args.upload[0], args.upload[1])
        log_user_actions('upload object', log_file)
    elif args.download:
        download_object(args.download[0], args.download[1], args.download[2])
        log_user_actions('download object', log_file)
    elif args.delobj:
        delete_objects(args.delobj[0], args.delobj[1])
        log_user_actions('delete object', log_file)
    elif args.delbkt:
        delete_bucket(args.delbkt)
        log_user_actions('delete bucket', log_file)

