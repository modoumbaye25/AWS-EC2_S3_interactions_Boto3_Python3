import boto3, ec2_s3


class DynamoDBActions:
    def __init__(self, log_file_name=''):
        self.dynamodb_client = boto3.client('dynamodb')
        self.my_log = ec2_s3.LogActions(log_file_name)

    def table_exists(self, table_name):
        tables = self.dynamodb_client.list_tables()
        if table_name in tables['TableNames']:
            return True
        else:
            return False

    def create_user_table(self, table_name):
        if not self.table_exists(table_name):
            self.dynamodb_client.create_table(
                AttributeDefinitions=[
                    {
                        'AttributeName': 'Username',
                        'AttributeType': 'S'
                    },
                ],
                TableName=table_name,
                KeySchema=[
                    {
                        'AttributeName': 'Username',
                        'KeyType': 'HASH'
                    },
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            )

    def add_user_to_table(self, table_name, user_name, email):
        try:
            self.dynamodb_client.put_item(
                TableName=table_name,
                Item={'Username': {'S': user_name}, 'Email': {'S': email}}
            )
        except self.dynamodb_client.exceptions.ResourceNotFoundException as e:
            print(e)
            self.my_log.log_user_actions('error', e)
            exit()

    def user_exits_in_table(self, table_name, item_name):
        try:
            users = self.dynamodb_client.get_item(
                TableName=table_name,
                Key={'Username': {'S': item_name}})
            if 'Item' in users:
                return True
            else:
                return False
        except self.dynamodb_client.exceptions.ResourceNotFoundException as e:
            print(e)
            self.my_log.log_user_actions('error', e)