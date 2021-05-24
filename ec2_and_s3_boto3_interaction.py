import argparse
from pprint import pprint
import openpyxl as xl
import os
import logging
import boto3
import botocore
logging.basicConfig(format='%(levelname)s:%(message)s')


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
            logging.error("Invalid instance name")
    else:
        list_instances = ec2_client.describe_instances()
        count = 0
        for each_instance in instances(list_instances)[0]:
            count += 1
            print("{} Instance ID: {} | Instance Type: {} | Instance State: {}".format(count, each_instance['InstanceId'], each_instance['InstanceType'], each_instance['State']['Name']))


def create_instances(num_of_instances, passed_image_id):
    ec2_resource = boto3.resource('ec2')
    ec2_client = boto3.client('ec2')

    amazon_linux_free_tier_ami = ec2_client.describe_images(
        Filters=[{'Name': 'description', 'Values': ['Amazon Linux 2 AMI 2.0.20210318.0 x86_64 HVM gp2']}])['Images']

    if len(amazon_linux_free_tier_ami) and not passed_image_id:
        image_id = amazon_linux_free_tier_ami[0]['ImageId']
    else:
        image_id = passed_image_id

    keypair_name = ec2_client.describe_key_pairs()['KeyPairs'][0]['KeyName']

    ec2_resource.create_instances(ImageId=image_id, InstanceType='t2.micro', KeyName=keypair_name, MaxCount=num_of_instances, MinCount=1)


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
    except botocore.exceptions.ClientError:
         logging.error("No available instances on your account or instances in a terminated state")


def create_instance_from_excel_sheet(excel_file_path):
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


def new_user(user_name):
    dynamodb_client = boto3.client('dynamodb')
    dynamodb_client.put_item(
        TableName='Boto3ScripUsers',
        Item={'Username': {'S': user_name}, 'Email': {'S': f'{user_name}@amazon.com'}}
    )
    print("""User {} created. Email generated: {}@amazon.com
    Welcome email sent to new user""".format(user_name, user_name))
    # new user being added to dynamodb table should invoke the WelcomeEmail lambda to send new user a welcome email


def autheticate_user(user):
    dynamodb_client = boto3.client('dynamodb')
    users = dynamodb_client.get_item(
    TableName='Boto3ScripUsers',
    Key={'Username': {'S': user}})

    user_exists = False
    if 'Item' in users:
        user_exists = True

    return user_exists


def create_s3_bucket(bucket_name):
    s3_client = boto3.client('s3')
    s3_client.create_bucket(
        ACL='private', Bucket=bucket_name,
        CreateBucketConfiguration={'LocationConstraint': 'us-west-2'})


def upload_object(bucket_name, file_path):
    file_name = os.path.split(file_path)
    s3_client = boto3.client('s3')
    s3_client.upload_file(file_path, bucket_name, file_name)


def list_buckets():
    s3_client = boto3.client('s3')
    my_buckets = s3_client.list_buckets()['Buckets']
    buckets = []
    for every_bucket in my_buckets:
        buckets.append(every_bucket)

    return buckets


def delete_objects(bucket_name, object_name):
    s3_client = boto3.client('s3')
    s3_client.delete_object(
        Bucket=bucket_name,
        Key=object_name,
    )


def delete_bucket(bucket_name):
    s3_client = boto3.client('s3')
    s3_client.delete_bucket(Bucket=bucket_name)


def download_object(bucket_name, object_name, destination_folder):
    s3_client = boto3.client('s3')
    destination_path = os.path.join(destination_folder, object_name)
    print(destination_path)
    s3_client.download_file(bucket_name, object_name, destination_path)


def list_objects(bucket_name):
    s3_client = boto3.client('s3')
    my_objects = s3_client.list_objects(Bucket=bucket_name)
    return my_objects['Contents']


if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=lambda prog: argparse.HelpFormatter(prog,max_help_position=70, width=1000, indent_increment=5), description="Interact with EC2 and S3")
    ec2_group = parser.add_argument_group('EC2 arguments')
    s3_group = parser.add_argument_group('S3 arguments')

    ec2_group.add_argument("-c", "--create", help="Launch instance, must pass the number of instances to launch or excel file, optionally pass desired AMI ID", metavar='NUMBER_OF_INSTANCES or EXCEL_FILE')
    ec2_group.add_argument("-l", "--list", action="store_true", help="List instances, pass instance ID to get more information on a specific instance")
    ec2_group.add_argument("-s", "--state", help="Change state of all instances unless instance ID is passed, must pass state to chage (stop, start, or terminate)", choices=['terminate', 'stop', 'run'], metavar='STATE')
    ec2_group.add_argument("-id", help="Pass instance ID or AMI ID", metavar='ID')

    parser.add_argument('-nu', '--newuser', help="Create new user, must pass new user's alias", metavar='USERNAME')
    parser.add_argument('-u', '--user', help="User authentication, must pass username to interact with S3 or EC2, leave blank and pass --newuser when crating a new user", required='True', nargs="?", const=" ", metavar='USERNAME')

    s3_group.add_argument('-cb', help="Create bucket, must pass bucket name", metavar='BUCKETNAME')
    s3_group.add_argument('-lb', help="List buckets", action="store_true")
    s3_group.add_argument('-lo', help="List objects/files in a particular bucket, must pass bucket name", metavar='BUCKET_NAME')
    s3_group.add_argument("--upload", nargs='+', help="Upload file to specified bucket, must pass bucket name and file path", metavar='FILE_NAME FILE_PATH')
    s3_group.add_argument("--download", nargs='+', help="Download object from a bucket, must pass bucket name, object name, and destination folder", metavar='BUCKET_NAME OBJECT_NAME DEST_FOLDER')
    s3_group.add_argument('--delobj', nargs='+', help="Delete object, must pass bucket name and object name", metavar='BUCKET_NAME OBJECT_NAME')
    s3_group.add_argument('--delbkt', help="Delete bucket, must pass bucket name", metavar='BUCKET_NAME')
    args = parser.parse_args()

    if autheticate_user(args.user):
        if args.list:
            list_instances(args.id)
        elif args.create:
            if args.create.isdigit():
                create_instances(int(args.create), args.id)
            else:
                create_instance_from_excel_sheet(args.create)
        elif args.state:
            if args.id:
                change_instance_state([args.id], args.state)
            else:
                ec2_client = boto3.client('ec2')
                instance_state_filter = [{'Name': 'instance-state-name', 'Values': ['pending', 'stopped', 'running', 'stopping']}]
                list_instances = ec2_client.describe_instances(Filters=instance_state_filter)
                my_instance_ids = instances(list_instances)[1]

                change_instance_state(my_instance_ids, args.state)
        elif args.cb:
            create_s3_bucket(args.cb)
        elif args.lb:
            for bucket in list_buckets():
                print('Bucket Name: {} | Date Created: {}'.format(bucket['Name'], bucket['CreationDate']))
        elif args.lo:
            objs = list_objects(args.lo)
            for obj in objs:
                print('{} | Size: {} KB | Last Modified: {}'.format(obj['Key'], obj['Size'], obj['LastModified']))
        elif args.upload:
            upload_object(args.upload[0], args.upload[1])
        elif args.download:
            download_object(args.download[0], args.download[1], args.download[2])
        elif args.delobj:
            delete_objects(args.delobj[0], args.delobj[1])
        elif args.delbkt:
            delete_bucket(args.delbkt)
    elif args.newuser:
            new_user(args.newuser)
    else:
        print("User does not exist, please enter a valid username or creat a new user")
