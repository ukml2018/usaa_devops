# Get token from API Getaway
#Validate token with Cognito
#Send signed new token with user and group name to Gloo
#Send policy or token to to API
#Autor : Uttam Manna 
import boto3
import json
import base64
#import requests
import hmac
import hashlib
import subprocess
import sys
import os
import datetime
#from cryptography.hazmat.primitives import serialization
#from cryptography.hazmat.backends import default_backend

# Install the PyJWT package using pip
subprocess.check_call([sys.executable, "-m", "pip", "install", "--target", "/tmp", "PyJWT"])
    
# Add the package to the Python path
sys.path.insert(0, '/tmp')
    
# Import the JWT module
import jwt   
print('import jwt from outside')

def lambda_handler(event, context):
    # Get the access token from the request headers
    print('*********** The event is: ***************')
    print(event)
    #auth_token = event['headers']['Authorization']
    #print(auth_token)
    #access_token = auth_token.split(' ')[1]
    access_token = event['authorizationToken'] 
    print(access_token)
    
    # Define the endpoint URL of the Gloo Gateway API
    #endpoint = 'https://your-gloo-gateway-url.com/your-api-endpoint'
    
    # Validate the access token using Amazon Cognito
    region = 'us-east-1'
    user_pool_id = 'us-east-1_JvnBSOtpn'
    client_id = '3avrvs5l0s3puad6v8vluug2j'
    cognito = boto3.client('cognito-idp', region_name=region)
    client_secret='1a9qp8edjcgrnrcsph3io9rk7t5g51k89iftiv6tns0qpcljqhmu'
    username='uttam.simplilearn@gmail.com'
    password='Usaa@123'
    user_id = 'd4b8c488-90d1-7025-6340-7bf155dd68a4'
    secret_hash = base64.b64encode(hmac.new(bytes(client_secret, 'utf-8'), bytes(username + client_id, 'utf-8'), digestmod=hashlib.sha256).digest()).decode()
    print(cognito)
    #form the token payload
    payload = {'sub': user_id}
    jwt_token = jwt.encode(payload, access_token, algorithm='HS256')
    print('Prining jwt token')
    print(jwt_token)
    cognito_token = authenticate_and_get_token(username, password,  user_pool_id, client_id, secret_hash, access_token,user_id )
    #cognito_token_client= generate_cognito_token_client(client_id, client_secret, user_pool_id)
    print(cognito_token)
    
    # Convert the payload to a JSON string
    cognito_token_json = json.dumps(cognito_token)

    # Parse the JSON string into a dictionary
    cognito_token__dict = json.loads(cognito_token_json)
    print('Printing Cognito Dictionary')
    print(cognito_token__dict)
     
    cognito_token_json = json.dumps(cognito_token)
    cognito_token_dict = json.loads(cognito_token_json)
    length=len(cognito_token_dict["ChallengeParameters"]["userAttributes"])
    userlen=cognito_token_dict["ChallengeParameters"]["userAttributes"]
    l=[]
    for i in range(10,length-2) :
        l.append(userlen[i])
    user_name = ''.join([str(n) for n in l])
    print('Prining Cognito User')
    print(user_name)
    
    
    auth = 'Deny'
    #if  access_token == 'testing' :
    if  access_token == user_name :
        auth = 'Allow'
    else:
        auth = 'Deny'
    
    # Extract the group name from the response
     
    try:
        data = cognito.admin_list_groups_for_user( 
                  UserPoolId=user_pool_id,
                  Username=username
                )
        groups = data['Groups']
        #print('Data response:', data)
        print('Group Details:', groups)
    except Exception as e:
        print('Error:', e)
        raise e
    
    print('Group Details outside:', groups)
    
    groups_json = json.dumps(groups, default=serialize_datetime)
    print('groups_json=',groups_json)
    groups_json_split=groups_json.split(',')[0]
    print('groups_json_split:',groups_json_split)
    length=len(groups_json_split)
    print('length,',length)
    l=[]
    for i in range(16,length-1) :
        l.append(groups_json_split[i])
    group_name = ''.join([str(n) for n in l])
    print('Prining Group name')
    print(group_name)
    
    #form the token payload
    payload_new = {'group_name':group_name}
    #payload_new = {"group_name":group_name, 
    #               "access_token" :access_token
    #              }
    #pem_bytes = b"-----BEGIN PRIVATE KEY-----\nMIGEAgEAMBAGByqGSM49AgEGBS..."
    #passphrase = b"your password"
    #private_key = serialization.load_pem_private_key(
    #pem_bytes, password=passphrase, backend=default_backend()
    #)
    private_key = b"-----BEGIN PRIVATE KEY-----\nMIGEAgEAMBAGByqGSM49AgEGBS..."
    jwt_token_new = jwt.encode(payload_new, private_key, algorithm='HS256', headers={"kid": "230498151c214b788dd97f22b85410a5"},)
    #To decode use jwt.decode(encoded, options={"verify_signature": False}) as above function has signed signature
    print('Prining new jwt token')
    print(jwt_token_new)
    # Return the new access token as the authorization context
    auth_context = {
        'access_token': jwt_token_new
    }
    
    print(auth_context)
    # Define the request headers and body
    headers = {
        'Content-Type': 'application/json'
    }
    body = json.dumps({
            'access_token': auth_context
        })
    print(body)
    # Send the request to the Gloo Gateway API
   #response = requests.post(endpoint, headers=headers, json=body)

    #return policy
    
    #authResponse = { "principalId": "abc123", "policyDocument": { "Version": "2012-10-17", "Statement": [{"Action": "execute-api:Invoke", "Resource": ["arn:aws:execute-api:us-east-1:783621988852:2wpsrqooj4/*/"], "Effect": auth}] }}

    #return authResponse
    policy_dtl= generate_policy('user', auth , event['methodArn'])
    #if you want to send token return jwt_token else retun policy_dtl
    #return generate_policy('user', auth , event['methodArn'])
    return policy_dtl
    #return jwt_token_new
    
#This function will return the valid policy

def generate_policy(principal_id, effect, resource, context=None):
    auth_response = {}
    auth_response['principalId'] = principal_id
    if effect and resource:
        policy_document = {}
        policy_document['Version'] = '2012-10-17'
        policy_statement = {}
        policy_statement['Action'] = 'execute-api:Invoke'
        policy_statement['Effect'] = effect
        policy_statement['Resource'] = resource
        if context:
            policy_statement['Context'] = context
        policy_document['Statement'] = [policy_statement]
        auth_response['policyDocument'] = policy_document
    return auth_response

#This function will return the Cognito connection payload
    
def authenticate_and_get_token(username: str, password: str, 
                               user_pool_id: str, app_client_id: str , secret_hash: str, sec_key: str, user_id) -> None:
    
    # Import the JWT module
    import jwt   
    #print('import jwt from submodule')
    client = boto3.client('cognito-idp')
    payload = {'sub': user_id}
    jwt_token = jwt.encode(payload, sec_key, algorithm='HS256')
    
    auth_params = {
        'TOKEN': jwt_token,
    }
    
    auth_flow_metadata = {
        'AuthParameters': {
            'ID_TOKEN': jwt_token,
        },
        'ClientMetadata': {
            'foo': 'bar',
        },
    }

    response = client.admin_initiate_auth(
        UserPoolId=user_pool_id,
        ClientId=app_client_id,
        AuthFlow='ADMIN_NO_SRP_AUTH',
        #AuthFlow="USER_PASSWORD_AUTH",
        AuthParameters={
            "USERNAME": username,
            "PASSWORD": password,
            "SECRET_HASH": secret_hash
        },
    )
    
    return response

# Define a custom function to serialize datetime objects
def serialize_datetime(obj):
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    raise TypeError("Type not serializable")
    
# Define tzlocal() to handle Json payload
def tzlocal() :
   return None
    
