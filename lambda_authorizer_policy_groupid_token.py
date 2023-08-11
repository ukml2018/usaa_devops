"""
Get token from API Getaway as pass through message from Gloo
Validate JWT token with Cognito information (group)
Send signed new token with user and group name to Gloo
Send token to to Gloo and Policy back to API Gateway
Author : Uttam Manna 
"""
import boto3
import json
import base64
import hmac
import hashlib
import subprocess
import sys
import os
import datetime

# Install the PyJWT package using pip
subprocess.check_call([sys.executable, "-m", "pip", "install", "--target", "/tmp", "PyJWT"])
    
# Add the package to the Python path
sys.path.insert(0, '/tmp')

#Install pip3.6 install requests
subprocess.check_call([sys.executable, "-m", "pip", "install", "--target", "/tmp", "requests"])

# Add the package to the Python path
sys.path.insert(0, '/tmp')
    
# Import the JWT module
import jwt   

# Import requests module
import requests

def lambda_handler(event, context):
    # Get the access token from the request headers
    print('*********** The event is: ***************')
    print(event)
    #auth_token = event['headers']['Authorization']
    #print(auth_token)
    #access_token = auth_token.split(' ')[1]
    access_token = event['authorizationToken'] 
    print(access_token)
    #gloo_token_data=access_token
    """
    #decode the token and get the user information
    #gloo_token_data = decode_gloo_token(access_token)
    #print('gloo_token_data=', gloo_token_data)
    
    #Retrieving UserId from the token
    # Sample token for testing eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkNGI4YzQ4OC05MGQxLTcwMjUtNjM0MC03YmYxNTVkZDY4YTQifQ.Q4FGRmUpRmIuW7BE7GGwUWXBTok-_JoYuyHjI04WZJQ
    #gloo_token_data= {'sub': 'd4b8c488-90d1-7025-6340-7bf155dd68a4'}
    #userid_str = json.dumps(gloo_token_data)
    #length=len(userid_str)
    #l=[]
    #for i in range(9,length-2) :
    #    l.append(userid_str[i])
    #gloo_userid = ''.join([str(n) for n in l])
    #print('Prining Gloo UserId=',gloo_userid)
    """
    #Extract Gloo groups from the token
    gloo_token_raw_data=decode_gloo_token(access_token)
    gloo_token_group_data=gloo_token_raw_data["groups"]
    print('gloo_token_group_data=', gloo_token_group_data) 
    groupid_str = json.dumps(gloo_token_group_data)
    length=len(groupid_str)
    l=[]
    for i in range(2,length-2) :
        l.append(groupid_str[i])
    gloo_groupid = ''.join([str(n) for n in l])
    print('Prining Gloo GroupId=',gloo_groupid)
    #Extract Gloo groups from the token
    
    # Define the endpoint URL of the Gloo Gateway API
    #endpoint = 'https://jwt.io/'
    endpoint = os.environ.get('endpoint')
    print('endpoint=',endpoint)
    # Validate the access token using Amazon Cognito
    #region = 'us-east-1'
    region  = os.environ.get('region')
    print('region=',region)
    #user_pool_id = 'us-east-1_JvnBSOtpn'
    user_pool_id = os.environ.get('user_pool_id')
    print('user_pool_id =',user_pool_id)
    #client_id = '3avrvs5l0s3puad6v8vluug2j'
    client_id = os.environ.get('client_id')
    print('client_id =',client_id)
    cognito = boto3.client('cognito-idp', region_name=region)
    #client_secret='1a9qp8edjcgrnrcsph3io9rk7t5g51k89iftiv6tns0qpcljqhmu'
    client_secret= os.environ.get('client_secret')
    print(' client_secret=', client_secret)
    #username='uttam.simplilearn@gmail.com'
    username= os.environ.get('username')
    print('username=',username)
    #password='Usaa@123'
    password= os.environ.get('password')
    print('password=',password)
    #user_id = 'd4b8c488-90d1-7025-6340-7bf155dd68a4'
    user_id = os.environ.get('user_id')
    print('user_id =',user_id)
    #user_id = gloo_userid
    secret_hash = base64.b64encode(hmac.new(bytes(client_secret, 'utf-8'), bytes(username + client_id, 'utf-8'), digestmod=hashlib.sha256).digest()).decode()
    #form the token payload
    payload = {'sub': user_id}
    jwt_token = jwt.encode(payload, access_token, algorithm='HS256')
    print('Prining jwt token=',jwt_token)
    cognito_token = authenticate_and_get_token(username, password,  user_pool_id, client_id, secret_hash, access_token,user_id )
    print('Cognito information=',cognito_token)
    
    # Convert the payload to a JSON string
    cognito_token_json = json.dumps(cognito_token)

    # Parse the JSON string into a dictionary
    cognito_token__dict = json.loads(cognito_token_json)
    print('Printing Cognito Dictionary=',cognito_token__dict)
   
    cognito_token_json = json.dumps(cognito_token)
    cognito_token_dict = json.loads(cognito_token_json)
    length=len(cognito_token_dict["ChallengeParameters"]["userAttributes"])
    userlen=cognito_token_dict["ChallengeParameters"]["userAttributes"]
    l=[]
    for i in range(10,length-2) :
        l.append(userlen[i])
    user_name = ''.join([str(n) for n in l])
    print('Prining Cognito email=',user_name)
    
    
    length=len(cognito_token_dict["ChallengeParameters"]["USER_ID_FOR_SRP"])
    userlen=cognito_token_dict["ChallengeParameters"]["USER_ID_FOR_SRP"]
    l=[]
    for i in range(0,length) :
        l.append(userlen[i])
    cognito_user_id = ''.join([str(n) for n in l])
    print('Prining Cognito User=',cognito_user_id)
    
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
    print('Prining Group name=',group_name)
    
    group_name = 'MEMBER' #this is for testing
    auth = 'Deny'
    #if  access_token == 'testing' :
    #if  access_token == user_name :
    #if cognito_user_id == gloo_userid :
    if group_name == gloo_groupid :
        auth = 'Allow'
    else:
        auth = 'Deny'
    
    #If validation is successful call gloo service
    if auth == 'Allow' or auth == 'Deny' :
       #form the token payload
       payload_new = {'group_name':group_name}
       private_key = b"-----BEGIN PRIVATE KEY-----\nMIGEAgEAMBAGByqGSM49AgEGBS..."
       jwt_token_new = jwt.encode(payload_new, private_key, algorithm='HS256', headers={"kid": "230498151c214b788dd97f22b85410a5"},)
       #To decode use jwt.decode(encoded, options={"verify_signature": False}) as above function has signed signature
       print('Prining new jwt token=',jwt_token_new)
       # Return the new access token as the authorization context
       auth_context = {
          'access_token': jwt_token_new
       }
       print('auth_context=',auth_context)
       # Define the request headers and body
       headers = {
           'Content-Type': 'application/json'
        }
       body = json.dumps({
              'access_token': jwt_token_new
        })
       # Send the request to the Gloo Gateway API
       print('POST valid token to Gloo end point')
       try:
          response = requests.post(endpoint, headers=headers, json=body)
          print('status code=',response.status_code)
       except Exception as e:
          print('Error:', e)
          raise e

    #return policy
    #return authResponse
    print('methodArn =',event['methodArn'])
    invoke_url = event['methodArn']
    invoke_url_split=invoke_url.split('/')[0]+'/'+'*'+'/'
    print(invoke_url_split)
    policy_dtl= generate_policy('user', auth , event['methodArn'], invoke_url_split)
    
    #if you want to send token return jwt_token else retun policy_dtl
    #return generate_policy('user', auth , event['methodArn'])
    return policy_dtl
    #return jwt_token_new
    
#This function will return the valid policy

def generate_policy(principal_id, effect, resource, invoke_url, context=None):
    auth_response = {}
    auth_response['principalId'] = principal_id
    if effect and resource:
        policy_document = {}
        policy_document['Version'] = '2012-10-17'
        policy_statement = {}
        policy_statement['Action'] = 'execute-api:Invoke'
        policy_statement['Effect'] = effect
        #policy_statement['Resource'] = resource
        policy_statement['Resource'] = invoke_url
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
   
#This function will decode the jwt token 
def decode_gloo_token(token: str):
    """
    :param token: jwt token
    :return:
    """
    decoded_data = jwt.decode(jwt=token,
                              key='secret',
                              algorithms=["RS512"],
                              options={"verify_signature": False})

    return decoded_data