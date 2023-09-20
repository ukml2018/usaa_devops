import json
import boto3

def lambda_handler(event, context):
    # Specify the user pool ID
    user_pool_id = 'us-east-1_JvnBSOtpn'

    # Specify the S3 bucket details
    bucket_name = 'cognitobackup2023'
    s3_client = boto3.client('s3')

    # Initialize the AWS Cognito Identity Provider client
    cognito_client = boto3.client('cognito-idp')

    # Restore user pool data
    user_pool_data = s3_client.get_object(Bucket=bucket_name, Key='user_pool_data.json')
    user_pool_data = json.loads(user_pool_data['Body'].read().decode('utf-8'))
    user_pool_data_modified = user_pool_data['UserPool']
    print('User Pool data modified=',user_pool_data_modified)
    #cognito_client.update_user_pool(UserPoolId=user_pool_id, **user_pool_data)
    #rename json attribute
    UserPoolId = user_pool_data_modified.pop('Id')
    #user_pool_data_modified['UserPoolId'] = field
    #user_pool_data_modified.pop('UserPoolId')
    #user_pool_data_modified.pop('Id')
    field=user_pool_data_modified.pop('Name')
    user_pool_data_modified['PoolName'] = field
    user_pool_data_modified.pop('CreationDate')
    user_pool_data_modified.pop('SchemaAttributes') 
    user_pool_data_modified.pop('UsernameAttributes')
    user_pool_data_modified.pop('EstimatedNumberOfUsers')
    user_pool_data_modified.pop('LastModifiedDate')
    user_pool_data_modified.pop('AdminCreateUserConfig')
    domain=user_pool_data_modified.pop('Domain')
    arn=user_pool_data_modified.pop('Arn')
    print("Test1 json=",user_pool_data_modified)
    #cognito_client.create_user_pool(UserPoolId=UserPoolId, **user_pool_data_modified)
    cognito_client.create_user_pool( **user_pool_data_modified)
    
    newUserPool = cognito_client.list_user_pools(MaxResults=1);
    print('New User Pool:',newUserPool)
    newClientID = newUserPool['UserPools'][0]['Id']
    print('New Client ID=',newClientID)
    # Restore user pool clients
    user_pool_clients = s3_client.get_object(Bucket=bucket_name, Key='user_pool_clients.json')
    user_pool_clients = json.loads(user_pool_clients['Body'].read().decode('utf-8'))
    user_pool_clients['UserPoolId']= newClientID
    
    print("User Pool client Json=",user_pool_clients)
    for client in user_pool_clients['UserPoolClients']:
        client.pop('ClientId')
        client['UserPoolId']=newClientID
        print('Client to be created=',client)
        #cognito_client.update_user_pool_client(UserPoolId=user_pool_id, ClientId=client['ClientId'], **client)
        #cognito_client.update_user_pool_client(**client)
        cognito_client.create_user_pool_client(**client,GenerateSecret=True,AllowedOAuthFlows=['client_credentials'])
        
    '''    
    #Update the client id
    for client in user_pool_clients['UserPoolClients']:
        #client.pop('ClientId')
        client['UserPoolId']=newClientID
        print('Client to be created=',client)
        #cognito_client.update_user_pool_client(UserPoolId=user_pool_id, ClientId=client['ClientId'], **client)
        cognito_client.update_user_pool_client(**client)
    '''
    
    # Restore resource servers
    resource_servers = s3_client.get_object(Bucket=bucket_name, Key='resource_servers.json')
    resource_servers = json.loads(resource_servers['Body'].read().decode('utf-8'))
    print("Json file for Resource server=",resource_servers)
    
    for server in resource_servers['ResourceServers']:
        #cognito_client.update_resource_server(UserPoolId=user_pool_id, Identifier=server['Identifier'], **server)
        #cognito_client.update_resource_server(**server)
        server['UserPoolId']=newClientID
        cognito_client.create_resource_server(**server)
    # Restore user groups
    user_groups = s3_client.get_object(Bucket=bucket_name, Key='user_groups.json')
    user_groups = json.loads(user_groups['Body'].read().decode('utf-8'))
    print("Json for user group=",user_groups)
    user_groups['Groups'][0].pop('LastModifiedDate')
    user_groups['Groups'][0].pop('CreationDate')
    print("Json for user group1=",user_groups)
    for group in user_groups['Groups']:
        #cognito_client.create_group(UserPoolId=user_pool_id, **group)
        group['UserPoolId']=newClientID
        cognito_client.create_group( **group)

    # Restore users
    users = s3_client.get_object(Bucket=bucket_name, Key='users.json')
    users = json.loads(users['Body'].read().decode('utf-8'))
    print("Json for users=",users)
    for user in users['Users']:
        #cognito_client.admin_create_user(UserPoolId=user_pool_id, **user)
        field=user.pop('Attributes')
        print('Field=',field)
        user['UserAttributes'] =field
        user['UserPoolId']=newClientID
        user.pop('UserCreateDate')
        user.pop('UserLastModifiedDate')
        user.pop('Enabled')
        user.pop('UserStatus')
        user['UserAttributes'].pop(0)
        print('User json inside For loop=',user)
        cognito_client.admin_create_user( **user)
    # Restore Cognito host domain
    cognito_host_domain = s3_client.get_object(Bucket=bucket_name, Key='cognito_host_domain.json')
    cognito_host_domain = json.loads(cognito_host_domain['Body'].read().decode('utf-8'))
    #cognito_client.update_user_pool_domain(Domain=user_pool_id, **cognito_host_domain)
    #cognito_client.update_user_pool_domain(domain)
    #cognito_client.create_user_pool_domain(UserPoolId=newClientID,Domain=domain, CustomDomainConfig={'CertificateArn': 'arn:aws:acm:region:123456789012:certificate'})
    cognito_client.create_user_pool_domain(UserPoolId=newClientID,Domain=domain)
    #cognito_client.update_user_pool_domain(UserPoolId=newClientID,Domain=domain, CustomDomainConfig=None)
    
    '''
    # Retrieve user pool clients
    user_pool_clients = cognito_client.list_user_pool_clients(UserPoolId=newClientID)
    for client in user_pool_clients['UserPoolClients']:
        client_id = client['ClientId']
        ClientName = client['ClientName']
        # Retrieve client secret from backup file
        client_secret_file = s3_client.get_object(Bucket=bucket_name, Key=f'client_secret_{ClientName}.json')
        client_secret_data = json.loads(client_secret_file['Body'].read().decode('utf-8'))
        client_secret = client_secret_data['UserPoolClient']['ClientSecret']

        # Update client configuration with recovered client secret
        cognito_client.update_user_pool_client(
            UserPoolId=newClientID,
            ClientId=client_id,
            ClientSecret=client_secret
        )
     '''
    return {
        'statusCode': 200,
        'body': json.dumps('Cognito recovery completed successfully!')
    }