from pprint import pprint
import boto3, botocore, ec2_s3


class EC2Actions:
    def __init__(self, log_file_name=''):
        self.ec2_client = boto3.client('ec2')
        self.ec2_resource = boto3.resource('ec2')
        self.my_log = ec2_s3.LogActions(log_file_name)

    # iterates through instances then returns instances and a list of instances IDs
    def instances(self, filter=''):
        if filter:
            try:
                list_of_instances = self.ec2_client.describe_instances(Filters=filter)
            except botocore.exceptions.ParamValidationError as e:
                print(e)
                self.my_log.log_user_actions('error', e)
                exit()
            except botocore.exceptions.ClientError as e:
                print(e)
                self.my_log.log_user_actions('error', e)
                exit()
        else:
            list_of_instances = self.ec2_client.describe_instances()

        my_instances = []
        my_instance_ids = []
        for item in list_of_instances['Reservations']:
            for each_instance in item['Instances']:
                my_instances.append(each_instance)
                my_instance_ids.append(each_instance['InstanceId'])
        return [my_instances, my_instance_ids]

    # iterates through instances and prints Instance ID, Type, and State for each instance
    def list_instances(self):
        count = 0
        for each_instance in self.instances()[0]:
            count += 1
            print(
                "{} Instance ID: {} | Instance Type: {} | Instance State: {}".format(count, each_instance['InstanceId'], each_instance['InstanceType'], each_instance['State']['Name']))

    # gets detailed information on a specific instance
    def instance_info(self, instance_id):
        try:
            list_instances = self.ec2_client.describe_instances(
                Filters=[{'Name': 'instance-id', 'Values': [instance_id]}])
            pprint(list_instances['Reservations'][0]['Instances'])
        except IndexError:
            print("Invalid instance ID was passed")
            self.my_log.log_user_actions('error', 'failed attempt to get instance info, invalid instance ID')

    # launches one or more instance with pre-defined specs
    def create_instances(self, num_of_instances):
        amazon_linux2_ami = self.ec2_client.describe_images(
            Filters=[{'Name': 'description', 'Values': ['Amazon Linux 2 AMI 2.0.20210318.0 x86_64 HVM gp2']}])['Images']
        image_id = amazon_linux2_ami[0]['ImageId']

        # fetches one of user's keypair names
        keypair_name = self.ec2_client.describe_key_pairs()['KeyPairs'][0]['KeyName']

        ec2_resource = boto3.resource('ec2')
        ec2_resource.create_instances(ImageId=image_id, InstanceType='t2.micro', KeyName=keypair_name,
                                      MaxCount=num_of_instances, MinCount=1)

    # launches one or more instances with user's defined specs
    def create_custom_instance(self):
        instance_type = input("Instance type: ")
        ami_id = input("AMI ID: ")
        subnet_id = input("Subnet ID: ")
        sg_id = input("Security group ID: ")
        num_of_instances = int(input("How many instances to launch? "))
        keypair = input("Key pair: ")
        try:
            self.ec2_resource.create_instances(ImageId=ami_id, InstanceType=instance_type, SecurityGroupIds=[sg_id],
                                               SubnetId=subnet_id, KeyName=keypair, MaxCount=num_of_instances,
                                               MinCount=1)
        except botocore.exceptions.ParamValidationError as e:
            print(e)
            self.my_log.log_user_actions('error', e)
        except botocore.exceptions.ClientError as e:
            print(e)
            self.my_log.log_user_actions('error', e)

    # stops, starts, or terminates given instance(s)
    def change_instance_state(self, instance_id, instance_state):
        try:
            if instance_state == 'start':
                self.ec2_client.start_instances(InstanceIds=instance_id)
                print("starting instance(s)...")
                self.ec2_client.get_waiter('instance_running').wait(InstanceIds=instance_id)
                print("Instance(s) are up and running")
            elif instance_state == 'stop':
                self.ec2_client.stop_instances(InstanceIds=instance_id)
                print("stopping instance(s)...")
                self.ec2_client.get_waiter('instance_stopped').wait(InstanceIds=instance_id)
                print("Instance(s) stopped")
            elif instance_state == 'terminate':
                self.ec2_client.terminate_instances(InstanceIds=instance_id)
                print("terminating instance(s)...")
                self.ec2_client.get_waiter('instance_terminated').wait(InstanceIds=instance_id)
                print("Instance(s)s terminated")
        except botocore.exceptions.ClientError as e:
            print(e)
            self.my_log.log_user_actions('error', e)
