#!/usr/bin/env python3
import argparse, ec2_s3


if __name__ == "__main__":

    my_ec2 = ec2_s3.EC2Actions()
    my_s3 = ec2_s3.S3Actions()
    my_dynamodb = ec2_s3.DynamoDBActions()

    dynamodb_table_name = 'Boto3ScriptUsers'
    my_dynamodb.create_user_table(dynamodb_table_name)

    my_log = ec2_s3.LogActions()
    my_log.upload_log_s3('ec2s3logs789')

    parser = argparse.ArgumentParser(
        formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=30, width=1000, indent_increment=5),
        description="Interact with EC2 and S3")

    parser.add_argument('--newuser', nargs='+', help="Adds newuser to dyanmodb table, pass new username and email",
                        metavar='USERNAME')
    parser.add_argument('-u', '--user', default="none", help="pass username", metavar='')

    ec2_group = parser.add_argument_group('EC2 arguments')
    ec2_group.add_argument("-c", "--create", help="Launch instance, pass the number of instances to launch or pass 'custom' to customise instance", metavar='')
    ec2_group.add_argument("-l", "--list", action="store_true",
                           help="List instances, pass instance ID for more information on an instance")
    ec2_group.add_argument("-s", "--state",
                           help="Change state of all instances unless instance ID is passed, pass state to chage to (stop, start, or terminate)", choices=['terminate', 'stop', 'start'], metavar='')
    ec2_group.add_argument("-id", help="Pass instance ID", metavar='')

    s3_group = parser.add_argument_group('S3 arguments')
    s3_group.add_argument('-cb', help="Create bucket, pass bucket name", metavar='')
    s3_group.add_argument('-lb', help="List buckets", action="store_true")
    s3_group.add_argument('-lo', help="List objects/files in a particular bucket, must pass bucket name", metavar='')
    s3_group.add_argument("--upload", nargs='+', help="Upload file to specified bucket, pass bucket name and file path", metavar='')
    s3_group.add_argument("--download", nargs='+', help="Download object from a bucket, pass bucket name, object name, and destination folder", metavar='')
    s3_group.add_argument('--delobj', nargs='+', help="Delete object, pass bucket name and object name", metavar='')
    s3_group.add_argument('--delbkt', help="Delete bucket, must pass bucket name", metavar='')
    args = parser.parse_args()

    if my_dynamodb.user_exits_in_table(dynamodb_table_name, args.user):
        if args.list:
            if args.id:
                my_ec2.instance_info(args.id)
            else:
                my_ec2.list_instances()
            my_log.log_user_actions('info', 'list instance', args.user)
        elif args.create:
            if args.create.isdigit():
                my_ec2.create_instances(int(args.create))
            elif args.create == 'custom'.lower():
                my_ec2.create_custom_instance()
            else:
                print("Error: Invalid input")
            my_log.log_user_actions('info', 'launch instance', args.user)
        elif args.state:
            if args.id:
                my_ec2.change_instance_state([args.id], args.state)
            else:
                non_terminated_instances_filter = [{'Name': 'instance-state-name', 'Values': ['pending', 'stopped', 'running', 'stopping']}]
                my_instance_ids = my_ec2.instances(non_terminated_instances_filter)[1]
                my_ec2.change_instance_state(my_instance_ids, args.state)
            my_log.log_user_actions('info', 'change instance state', args.user)
        elif args.cb:
            my_s3.create_s3_bucket(args.cb)
            my_log.log_user_actions('info', 'create s3 bucket', args.user)
        elif args.lb:
            for bucket in my_s3.list_buckets():
                print('Bucket Name: {} | Date Created: {}'.format(bucket['Name'], bucket['CreationDate']))
            my_log.log_user_actions('info', 'list bucket', args.user)
        elif args.lo:
            my_s3.list_objects(args.lo)
            my_log.log_user_actions('info', 'list object', args.user)
        elif args.upload:
            my_s3.upload_object(args.upload[0], args.upload[1])
            my_log.log_user_actions('info', 'upload object', args.user)
        elif args.download:
            my_s3.download_object(args.download[0], args.download[1], args.download[2])
            my_log.log_user_actions('info', 'download object', args.user)
        elif args.delobj:
            my_s3.delete_objects(args.delobj[0], args.delobj[1])
            my_log.log_user_actions('info', 'delete object', args.user)
        elif args.delbkt:
            my_s3.delete_bucket(args.delbkt)
            my_log.log_user_actions('info', 'delete bucket', args.user)
    elif args.newuser:
        my_dynamodb.add_user_to_table(dynamodb_table_name, args.newuser[0], args.newuser[1])
        my_log.log_user_actions('info', 'create user', args.newuser)
    else:
        print("Please pass a valid username or create a new user")
        my_log.log_user_actions('warning', 'attempted interaction with invalid user passed')


