import json
import boto3
import datetime
# Define a custom function to serialize datetime objects
def serialize_datetime(obj):
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    raise TypeError("Type not serializable")
    
# Define tzlocal() to handle Json payload
def tzlocal() :
   return None

def lambda_handler(event, context):
    # Specify the user pool ID
    user_pool_id = 'us-east-1_JvnBSOtpn'

    # Specify the S3 bucket details
    bucket_name = 'cognitobackup2023'
    s3_client = boto3.client('s3')

    # Initialize the AWS Cognito Identity Provider client
    cognito_client = boto3.client('cognito-idp')

    # Backup user pool data
    user_pool_data = cognito_client.describe_user_pool(UserPoolId=user_pool_id)
    s3_client.put_object(
        Bucket=bucket_name,
        Key='user_pool_data.json',
        Body=json.dumps(user_pool_data, indent=4,default=serialize_datetime)
    )

    # Backup user pool clients
    user_pool_clients = cognito_client.list_user_pool_clients(UserPoolId=user_pool_id)
    s3_client.put_object(
        Bucket=bucket_name,
        Key='user_pool_clients.json',
        Body=json.dumps(user_pool_clients, indent=4, default=serialize_datetime)
    )
    
    for client in user_pool_clients['UserPoolClients']:
        client_id = client['ClientId']
        ClientName = client['ClientName']

        # Backup client secret
        client_secret = cognito_client.describe_user_pool_client(UserPoolId=user_pool_id, ClientId=client_id)
        s3_client.put_object(
            Bucket=bucket_name,
            #Key=f'client_secret_{client_id}.json',
            Key=f'client_secret_{ClientName}.json',
            Body=json.dumps(client_secret, indent=4,default=serialize_datetime)
        )
        '''
        # Backup custom scopes for app client
        custom_scopes = cognito_client.list_scopes(
            UserPoolId=user_pool_id,
            ClientId=client_id
        )
        s3_client.put_object(
            Bucket=bucket_name,
            Key=f'custom_scopes_{client_id}.json',
            Body=json.dumps(custom_scopes, indent=4, default=serialize_datetime)
        )
        '''

    # Backup resource servers
    resource_servers = cognito_client.list_resource_servers(UserPoolId=user_pool_id, MaxResults=40)
    s3_client.put_object(
        Bucket=bucket_name,
        Key='resource_servers.json',
        Body=json.dumps(resource_servers, indent=4, default=serialize_datetime)
    )
    '''
    for server in resource_servers['ResourceServers']:
        server_identifier = server['Identifier']

        # Backup custom scopes for resource server
        custom_scopes = cognito_client.list_scopes(
            UserPoolId=user_pool_id,
            ResourceServerIdentifier=server_identifier
        )
        s3_client.put_object(
            Bucket=bucket_name,
            Key=f'custom_scopes_{server_identifier}.json',
            Body=json.dumps(custom_scopes, indent=4)
        )
    '''    
    # Backup user groups
    user_groups = cognito_client.list_groups(UserPoolId=user_pool_id)
    s3_client.put_object(
        Bucket=bucket_name,
        Key='user_groups.json',
        Body=json.dumps(user_groups, indent=4, default=serialize_datetime)
    )

    # Backup users
    users = cognito_client.list_users(UserPoolId=user_pool_id)
    s3_client.put_object(
        Bucket=bucket_name,
        Key='users.json',
        Body=json.dumps(users, indent=4, default=serialize_datetime)
    )

    # Backup Cognito host domain
    cognito_host_domain = cognito_client.describe_user_pool_domain(Domain=user_pool_id)
    s3_client.put_object(
        Bucket=bucket_name,
        Key='cognito_host_domain.json',
        Body=json.dumps(cognito_host_domain, indent=4, default=serialize_datetime)
    )

    return {
        'statusCode': 200,
        'body': json.dumps('Backup completed successfully!')
    }