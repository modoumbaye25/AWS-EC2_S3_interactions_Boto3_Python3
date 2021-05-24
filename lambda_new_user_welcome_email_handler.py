import json
import boto3

ses_client = boto3.client('ses')


def lambda_handler(event, context):
    def handle_new_user(record):
        new_user = record['dynamodb']['NewImage']

        new_user_email = new_user['Email']['S']

        my_email_address = ses_client.list_verified_email_addresses()['VerifiedEmailAddresses'][0]

        ses_client.send_email(
            Source=my_email_address,
            Destination={'ToAddresses': [new_user_email]},
            Message={'Subject': {'Data': 'Welcome'},
                     'Body': {'Text': {'Data': 'Welcome! Your Boto3 Script user account have been created'}}}
        )

    for each_record in event['Records']:
        if each_record['eventName'] == 'INSERT':
            handle_new_user(each_record)

