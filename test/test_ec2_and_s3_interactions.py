# This is just a basic unit test, not a full test

from unittest import TestCase
from ec2_and_s3_boto3_interaction import instances

sample = {'Reservations': [{'Instances': [{'ImageId': 'ami-123',
                                        'InstanceId': 'i-123',
                                        'InstanceType': 't2.micro',
                                        'State': {'Code': 0, 'Name': 'pending'}},

                                       {'ImageId': 'ami-098',
                                        'InstanceId': 'i-098',
                                        'InstanceType': 't2.micro',
                                        'KeyName': 'keypair',
                                        'State': {'Code': 0, 'Name': 'pending'}
                                        }
                                       ]
                         }
                        ]
       }


class Test(TestCase):

    # should pass
    def test_instances(self):
        instances_list = instances(sample)
        self.assertTrue('i-123' in instances_list[1])

    # should fail
    def test_instances(self):
        instances_list = instances(sample)
        self.assertFalse('i-321' in instances_list[1])
