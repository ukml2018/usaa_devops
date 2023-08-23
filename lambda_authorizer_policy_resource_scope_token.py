'''
Get token from API Getaway as pass through message from Gloo to lambda authorizer
Lambda Authorizer call the cognito authorizer with the same passthrough token
Cognito then return only the valid scopes out of all the scopes in the client token
Lambda authorizer then enrich the id-claim token with the valid scopes and token expiry dates from cognito
Send signed new/Refresh token to Gloo API service
Send Policy back to API Gateway
Author : Uttam Manna 
'''
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

#Install pip to install requests
subprocess.check_call([sys.executable, "-m", "pip", "install", "--target", "/tmp", "requests"])

# Add the package to the Python path
sys.path.insert(0, '/tmp')
    
# Import the JWT module
import jwt   

# Import requests module
import requests

#initialization of status code
statuscode = 200

def lambda_handler(event, context):
    # Get the access token from the request headers
    print('*********** The event is: ***************')
    print(event)
    access_token = event['authorizationToken'] 
    print(access_token)

    # Get the access token from the request headers
    #access_token = event['headers']['Authorization'].split(' ')[1]
    #gloo_token_data=access_token    
    # decode the token and get the user information
    #gloo_token_data = decode_gloo_token(access_token)
    #print('gloo_token_data=', gloo_token_data) 
    #Sample token to test
    '''
    -- Sample token for client id 3avrvs5l0s3puad6v8vluug2j
    eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsImtpZCI6IjIzMDQ5ODE1MWMyMTRiNzg4ZGQ5N2YyMmI4NTQxMGE1In0.eyJ0b2tlbl9uYW1lIjoiaWRfY2xhaW0iLCJzdWIiOiJhZTY3NzY2NC04MjdhLTRmYTUtYjM3Yy1lMzBhYmFmOWZhMzAiLCJuYmYiOjE2OTE1MjE5ODgsImlzcyI6IndzZGV2aW50ZXJuYWwudXNhYS5jb20iLCJleHBpcmVzX2luIjo2MDAsImlhdCI6MTcwMDM4ODQ2MSwiZXhwIjoxNzAwMzg4NDYxLCJwYXJ0eV9pZCI6IjMxMDgxIiwicGFydHlfdHlwZSI6IlVTQUEiLCJhdWQiOiJyc3ZjaW50LnVzYWEuY29tIiwianRpIjoiYzFiMjA0NTctY2ZjZi00MWQ4LTkyYTQtNDI2ZWJiNThmMTYyIiwidG9rZW5fdHlwZSI6Imp3dCIsInJlYWxtIjoibWVtYmVyIiwiZ3JvdXBzIjpbIk1FTUJFUiJdLCJjbGllbnRfaWQiOiIzYXZydnM1bDBzM3B1YWQ2djh2bHV1ZzJqIiwiY3VzdG9tZXNjb3BlIjpbInVzYWFfcmVzb3VyY2Vfc2VydmVyL3JlYWRfcHJvZHVjdCB1c2FhX3Jlc291cmNlX3NlcnZlci9jcmVhdGVfcHJvZHVjdCB1c2FhX3Jlc291cmNlX3NlcnZlci9kZWxldGVfcHJvZHVjdCJdLCJwcmVmaXgiOiJmb29fdXNhYV9ncnAifQ.X0RYr8Em7Tqfais920gpvRz5DFzN5BSy7dl-GHgae-Y
    '''  
    #Extract Gloo groups from the token
    gloo_token_raw_data=decode_gloo_token(access_token, 'y')
    '''
    gloo_token_group_data=gloo_token_raw_data["groups"]
    print('gloo_token_group_data=', gloo_token_group_data) 
    groupid_str = json.dumps(gloo_token_group_data)
    length=len(groupid_str)
    l=[]
    for i in range(2,length-2) :
        l.append(groupid_str[i])
    gloo_groupid = ''.join([str(n) for n in l])
    print('Prining Gloo GroupId=',gloo_groupid)
    '''
    # Extract scopes from token
    gloo_token_customscope_data=gloo_token_raw_data["customescope"]
    print('gloo_token_customscope_data=',gloo_token_customscope_data)
    client_scope= gloo_token_customscope_data[0].split(" ")
    print('Client scope=',client_scope)
    client_id=gloo_token_raw_data["client_id"]
    print('client id=',client_id)
    #Extract Gloo groups from the token
    
    # Define the endpoint URL of the Gloo Gateway API
    #endpoint = 'https://jwt.io/'
    endpoint = os.environ.get('endpoint')
    print('endpoint=',endpoint)
    #Define Cognito Host URL
    #hosturl = 'https://usaa-domain99999.auth.us-east-1.amazoncognito.com/oauth2/token'
    cognitohosturl = os.environ.get('cognitohosturl')
    print('cognitohosturl=',cognitohosturl)
    # Validate the access token using Amazon Cognito
    #region = 'us-east-1'
    region  = os.environ.get('region')
    print('region=',region)
    #user_pool_id = 'us-east-1_JvnBSOtpn'
    user_pool_id = os.environ.get('user_pool_id')
    print('user_pool_id =',user_pool_id)
    #client_id = '3avrvs5l0s3puad6v8vluug2j'
    #client_id = os.environ.get('client_id')
    print('client_id =',client_id)
    cognito = boto3.client('cognito-idp', region_name=region)
    #client_secret='1a9qp8edjcgrnrcsph3io9rk7t5g51k89iftiv6tns0qpcljqhmu'
    #client_secret= os.environ.get('client_secret')
    client_secret=get_cognito_client_secret(client_id, user_pool_id)
    print(' client_secret=', client_secret)
   
    # Set the grant type to client_credentials
    grant_type = 'client_credentials'

    # Set the headers and payload
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    payload = {
        'grant_type': grant_type,
        'client_id': client_id,
        'client_secret': client_secret
        #'scope': ' '.join(client_scope)
    }

    # Send the POST request to get the access token
    response = requests.post(cognitohosturl, headers=headers, data=payload)
    #response = requests.post(cognitohosturl,  data=payload)
    print('response status code from cognito=',response.status_code)

    if response.status_code == 200:
        # Access token obtained successfully
        #access_token = response.json()['access_token']
        cognito_scope_token = response.json()['access_token']
        # Use the access token for further operations
        # e.g., calling other APIs or accessing protected resources
        # If statement for scope validation
        print('cognito_scope_token =',cognito_scope_token)
        cognito_scope_token_raw_data=decode_gloo_token(cognito_scope_token, 'n')
        cognito_scope_token_data=cognito_scope_token_raw_data["scope"]
        print('cognito_token_group_data=',cognito_scope_token_data)
        cognito_token_iss=cognito_scope_token_raw_data["iss"]
        print('cognito_token_iss=',cognito_token_iss)
        cognito_token_iat=cognito_scope_token_raw_data["iat"]
        print('cognito_token_iat=',cognito_token_iat)
        cognito_token_exp=cognito_scope_token_raw_data["exp"]
        print('cognito_token_exp=',cognito_token_exp)
        cognito_token_auth_time=cognito_scope_token_raw_data["auth_time"]
        print('cognito_token_exp=',cognito_token_auth_time)
        cognito_scope_token_data_list=cognito_scope_token_data.split()
        print('cognito_scope_token_data_list=',cognito_scope_token_data_list)

        # Check the custom scope in the user's scopes
        scope_valid = False
        numberOfScope=len(client_scope)
        #Store valid scope in newScope and invalid scope in invalidScope
        newScope=[]
        invalidScope=[]
        for iScope in range (numberOfScope) :
             if client_scope[iScope] in cognito_scope_token_data_list :
                scope_valid = True
                newScope.append(client_scope[iScope])
                print('New Scope=',newScope)
             else :
                scope_valid = False
                invalidScope.append(client_scope[iScope])
        print('Scope validation status=',scope_valid)
        scope_valid = True  # Return policy will be always true
        if scope_valid:
            # Authorized - Custom scope is valid
            auth = 'Allow'
            status_code = 200
            bodymsg=  'Access Granted'            
        else:
            # Unauthorized - Custom scope is not valid
            auth = 'Deny'
            status_code = 403
            bodymsg=  'Access Denied'            
    else:
        # Failed to obtain access token
        auth = 'Deny'
        status_code = response.status_code
        bodymsg=  'Failed to obtain access token'        
    print('statuscode=',status_code)
    print('bodymsg=', bodymsg)
    
    #If validation is successful call gloo service. Currently allowing all validations are sending call to Gloo
    if auth == 'Allow' or auth == 'Deny' :
       #form the token payload
       private_key = b"-----BEGIN PRIVATE KEY-----\nMIGEAgEAMBAGByqGSM49AgEGBS..."
       payload_json_str = json.dumps(gloo_token_raw_data)
       payload_data = json.loads(payload_json_str)
       payload_data["iss"]=cognito_token_iss
       payload_data["iat"]=cognito_token_iat
       payload_data["exp"]=cognito_token_exp
       payload_data["client_id"]=client_id
       payload_data["customescope"]=newScope
       payload_new = {"auth_time" : cognito_token_auth_time}
       payload_data.update(payload_new)
       print('New data payload =',payload_data)
       # Create Refresh Token
       jwt_token_new = jwt.encode(payload_data, private_key, algorithm='HS256', headers={"kid": "230498151c214b788dd97f22b85410a5"},)
       #To decode use jwt.decode(encoded, options={"verify_signature": False}) as above function has signed signature
       print('Prining new jwt token=',jwt_token_new)
            
       # Return the new access token as the authorization context
       auth_context = {
          'access_token': jwt_token_new
       }
       print('auth_context=',auth_context)
       #Create Body of the message
       reponse_token=json.dumps(retrun_response('user', status_code, bodymsg, jwt_token_new))
       # Define the request headers and body
       headers = {
           #'Content-Type': 'application/json'
           'Authorization': 'Bearer ' + jwt_token_new
        }
       body = json.dumps({
              #'access_token': jwt_token_new
              'body' : reponse_token
              #'body' : 'Refresh bearer Token After Cognito Authorization'
        })
       print('Gloo API header=',headers)
       print('Gloo API Body=', body)
       # Send the request to the Gloo Gateway API
       print('POST valid token to Gloo end point')
       try:
          response = requests.post(endpoint, headers=headers, json=body)
          print('status code=',response.status_code)
          print('Response from Gloo API=',response)
          #print('Content=',response.content)
       except Exception as e:
          print('Error:', e)
          raise e
    
    else:
        jwt_token_new =access_token
    
    #return policy
    #return authResponse
    print('methodArn =',event['methodArn'])
    invoke_url = event['methodArn']
    invoke_url_split=invoke_url.split('/')[0]+'/'+'*'+'/'
    print(invoke_url_split)
    policy_dtl= generate_policy('user', auth , event['methodArn'], invoke_url_split,jwt_token_new)
    print('Policy details=', policy_dtl)
    print('Before reponse token to be sent to API Gateway')
    print('statuscode=',status_code)
    print('bodymsg=', bodymsg)
    print('Token=',jwt_token_new)
    reponse_token=json.dumps(retrun_response('user', status_code, bodymsg, jwt_token_new))
    
    print('reponse_token=',reponse_token)
    #if you want to send token return jwt_token else retun policy_dtl
    #return generate_policy('user', auth , event['methodArn'])
    return policy_dtl
    
    '''
    return {
        'statusCode': status_code,
        'headers': {
            'Authorization': 'Bearer ' + jwt_token_new
        },
        'body': bodymsg
    }
    '''
    '''
    #return jwt_token_new
    #return reponse_token
    #response = {'result': reponse_token}
    #return response
    
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": reponse_token
    }
    '''

#This function return refresh token

def retrun_response(principal_id,statuscd, bodymsg, token, context=None):
    auth_response = {}
    auth_response['principalId'] = principal_id
    if statuscd and token :
       return_message = {} 
       #return_message['Version'] = '2012-10-17'
       return_statement = {}
       return_statement ['Statuscode'] = statuscd
       return_statement['Body'] = bodymsg
       return_statement['id-token'] = token
       if context:
            return_statement['Context'] = context
       return_message['Statement'] = [return_statement]
       auth_response['returnMessage'] = return_message
    return auth_response
    
    
#This function will return the valid policy

def generate_policy(principal_id, effect, resource, invoke_url, token, context=None ):
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
        #policy_statement['AccessToken'] = token
        if context:
            policy_statement['Context'] = context
        policy_document['Statement'] = [policy_statement]
        auth_response['policyDocument'] = policy_document
    return auth_response

#This function will return the Cognito connection payload
    
def authenticate_and_get_token(username: str, password: str,  user_pool_id: str, app_client_id: str , secret_hash: str, sec_key: str, user_id) -> None:
    
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
        AuthParameters={
            "USERNAME": username,
            "PASSWORD": password,
            "SECRET_HASH": secret_hash
        },
    )
    
    return response
    
#Get Refresh token
def authenticate_and_get_refresh_token ( user_pool_id: str, app_client_id: str , secret_hash: str, sec_key: str, group_name: str, auth_token) -> None:
    
    # Import the JWT module
    import jwt   
    #print('import jwt from submodule')
    client = boto3.client('cognito-idp')
    payload = {'sub': group_name}
    jwt_token = jwt.encode(payload, sec_key, algorithm='HS256', headers={"kid": "230498151c214b788dd97f22b85410a5"},)
    
    response = client.admin_initiate_auth(
        UserPoolId=user_pool_id,
        ClientId=app_client_id,
        AuthFlow='REFRESH_TOKEN_AUTH',
        AuthParameters={
            'REFRESH_TOKEN': auth_token,
            'CLIENT_ID': app_client_id,
            "DEVICE_KEY" : 'null',
            'SECRET_HASH': secret_hash
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
def decode_gloo_token(token: str , aud_flag: str):
    """
    :param token: jwt token
    :return:
    """
    if aud_flag == 'y' :
      decoded_data = jwt.decode(jwt=token,
                              key='secret',
                              algorithms=["RS512"],
                              audience="rsvcint.usaa.com",
                              options={"verify_signature": False})
    else :
      decoded_data = jwt.decode(jwt=token,
                              key='secret',
                              algorithms=["RS512"],
                              options={"verify_signature": False}) 
    return decoded_data
    
#This function will dynamically retrive the client secret based on client id from client credential token
def get_cognito_client_secret(app_client_id, cognito_userpool_id):
    client = boto3.client('cognito-idp')
    
    try:
        response = client.describe_user_pool_client(
            UserPoolId=cognito_userpool_id,
            ClientId=app_client_id
        )
        client_secret = response['UserPoolClient']['ClientSecret']
        return client_secret
    except Exception as e:
        print("Error:", e)
        return None