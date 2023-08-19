'''
Get token from API Getaway as pass through message from Gloo
Validate JWT token with Cognito information (group, scopes)
Send signed new/Refresh token e to Gloo
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
    eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsImtpZCI6IjIzMDQ5ODE1MWMyMTRiNzg4ZGQ5N2YyMmI4NTQxMGE1In0.eyJ0b2tlbl9uYW1lIjoiaWRfY2xhaW0iLCJzdWIiOiJhZTY3NzY2NC04MjdhLTRmYTUtYjM3Yy1lMzBhYmFmOWZhMzAiLCJuYmYiOjE2OTE1MjE5ODgsImlzcyI6IndzZGV2aW50ZXJuYWwudXNhYS5jb20iLCJleHBpcmVzX2luIjo2MDAsImlhdCI6MTcwMDM4ODQ2MSwiZXhwIjoxNzAwMzg4NDYxLCJwYXJ0eV9pZCI6IjMxMDgxIiwicGFydHlfdHlwZSI6IlVTQUEiLCJhdWQiOiJyc3ZjaW50LnVzYWEuY29tIiwianRpIjoiYzFiMjA0NTctY2ZjZi00MWQ4LTkyYTQtNDI2ZWJiNThmMTYyIiwidG9rZW5fdHlwZSI6Imp3dCIsInJlYWxtIjoibWVtYmVyIiwiZ3JvdXBzIjpbIk1FTUJFUiJdLCJjdXN0b21lc2NvcGUiOlsidXNhYV9yZXNvdXJjZV9zZXJ2ZXIvcmVhZF9wcm9kdWN0IiwidXNhYV9yZXNvdXJjZV9zZXJ2ZXIvY3JlYXRlX3Byb2R1Y3QiLCJ1c2FhX3Jlc291cmNlX3NlcnZlci9kZWxldGVfcHJvZHVjdCJdLCJwcmVmaXgiOiJmb29fdXNhYV9ncnAifQ.Srr6ildvdfmBUZ5l6_3HVg16dHQT9jUegKsBFVju6D4'
    '''  
    #Extract Gloo groups from the token
    gloo_token_raw_data=decode_gloo_token(access_token, 'y')
    gloo_token_group_data=gloo_token_raw_data["groups"]
    print('gloo_token_group_data=', gloo_token_group_data) 
    groupid_str = json.dumps(gloo_token_group_data)
    length=len(groupid_str)
    l=[]
    for i in range(2,length-2) :
        l.append(groupid_str[i])
    gloo_groupid = ''.join([str(n) for n in l])
    print('Prining Gloo GroupId=',gloo_groupid)
    # Extract scopes from token
    gloo_token_customscope_data=gloo_token_raw_data["customescope"]
    print('gloo_token_customscope_data=',gloo_token_customscope_data)
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
    '''
    payload = {'sub': user_id}
    jwt_token = jwt.encode(payload, access_token, algorithm='HS256')
    print('Prining jwt token=',jwt_token)
    cognito_token = authenticate_and_get_token(username, password,  user_pool_id, client_id, secret_hash, access_token,user_id )
    print('Cognito information=',cognito_token)
    session_token=cognito_token["Session"]
    
    # Convert the payload to a JSON string
    cognito_token_json = json.dumps(cognito_token)

    # Parse the JSON string into a dictionary
    cognito_token__dict = json.loads(cognito_token_json)
    print('Printing Cognito Dictionary=',cognito_token__dict)
   
    cognito_token_json = json.dumps(cognito_token)
    cognito_token_dict = json.loads(cognito_token_json)
    length=len(cognito_token_dict["ChallengeParameters"]["userAttributes"])
    userattributes=cognito_token_dict["ChallengeParameters"]["userAttributes"]
    l=[]
    for i in range(34,length-2) :
        l.append(userattributes[i])
    cognito_email = ''.join([str(n) for n in l])
    print('Prining Cognito email=',cognito_email)
    
    
    length=len(cognito_token_dict["ChallengeParameters"]["USER_ID_FOR_SRP"])
    userlen=cognito_token_dict["ChallengeParameters"]["USER_ID_FOR_SRP"]
    l=[]
    for i in range(0,length) :
        l.append(userlen[i])
    cognito_user_id = ''.join([str(n) for n in l])
    print('Prining Cognito User=',cognito_user_id)
    '''
    
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
    
      
    '''
    # Access session token
    session_token=cognito_token["Session"]
    print('Extract Session Token=',session_token)
    session_token_raw_data=jwt.decode(jwt=session_token,options={"verify_signature": False})
    print('Session token raw data=', session_token_raw_data) 
    '''
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
    }

    # Send the POST request to get the access token
    response = requests.post(cognitohosturl, headers=headers, data=payload)
    print('response from cognito=',response)

    if response.status_code == 200:
        # Access token obtained successfully
        #access_token = response.json()['access_token']
        cognito_scope_token = response.json()['access_token']
        #cognito_access_token = response_data["scope"]
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
        cognito_scope_token_data_list=cognito_scope_token_data.split()
        print('cognito_scope_token_data_list=',cognito_scope_token_data_list)

        # Check the custom scope in the user's scopes
        scope_valid = False
        numberOfScope=len(gloo_token_customscope_data)
        for iScope in range (numberOfScope) :
             if gloo_token_customscope_data[iScope] in cognito_scope_token_data_list :
                scope_valid = True
             else :
                scope_valid = False
        print('Scope validation status=',scope_valid)
        if scope_valid:
            # Authorized - Custom scope is valid
            auth = 'Allow'
            status_code = 200
            bodymsg=  'Access Granted'
            '''
            return {
                'statusCode': 200,
                'body': 'Access Granted'
            }
            '''
        else:
            # Unauthorized - Custom scope is not valid
            auth = 'Deny'
            status_code = 403
            bodymsg=  'Access Denied'
            '''
            return {
                'statusCode': 403,
                'body': 'Access Denied'
            }
            
        return {
            'statusCode': 200,
            'body': 'Access token obtained successfully'
        }
        '''
    else:
        # Failed to obtain access token
        auth = 'Deny'
        status_code = response.status_code
        bodymsg=  'Failed to obtain access token'
        '''
        return {
            'statusCode': response.status_code,
            'body': 'Failed to obtain access token'
        }
        '''
    print('statuscode=',status_code)
    print('bodymsg=', bodymsg)
    
    #If validation is successful call gloo service
    if auth == 'Allow' :
       #form the token payload
       payload_new = {'group_name':group_name}
       private_key = b"-----BEGIN PRIVATE KEY-----\nMIGEAgEAMBAGByqGSM49AgEGBS..."
       #jwt_token_new = jwt.encode(payload_new, private_key, algorithm='HS256', headers={"kid": "230498151c214b788dd97f22b85410a5"},)
       payload_json_str = json.dumps(gloo_token_raw_data)
       payload_data = json.loads(payload_json_str)
       #payload_new = {"user_id":cognito_user_id , "email":cognito_email}
       #payload_data.update(payload_new)
       #print('New data payload =',payload_data)
       payload_data["iss"]=cognito_token_iss
       payload_data["iat"]=cognito_token_iat
       payload_data["exp"]=cognito_token_exp
       jwt_token_new = jwt.encode(payload_data, private_key, algorithm='HS256', headers={"kid": "230498151c214b788dd97f22b85410a5"},)
       #To decode use jwt.decode(encoded, options={"verify_signature": False}) as above function has signed signature
       print('Prining new jwt token=',jwt_token_new)
       
       # Create Refresh Token
       #cognito_refresh_token=authenticate_and_get_refresh_token ( user_pool_id, client_id, secret_hash, private_key, group_name,session_token)
       #session_token=cognito_token["Session"]
       #print('Extract Session Token=',cognito_refresh_token)
       
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
    
    else:
        jwt_token_new =access_token
    
    #return policy
    #return authResponse
    print('methodArn =',event['methodArn'])
    invoke_url = event['methodArn']
    invoke_url_split=invoke_url.split('/')[0]+'/'+'*'+'/'
    print(invoke_url_split)
    policy_dtl= generate_policy('user', auth , event['methodArn'], invoke_url_split)
    print('Policy details=', policy_dtl)
    print('Before reponse token to be sent to API Gateway')
    print('statuscode=',status_code)
    print('bodymsg=', bodymsg)
    print('Token=',jwt_token_new)
    reponse_token= retrun_response(status_code, bodymsg, jwt_token_new)
    print('reponse_token=',reponse_token)
    #if you want to send token return jwt_token else retun policy_dtl
    #return generate_policy('user', auth , event['methodArn'])
    #return policy_dtl
    #return jwt_token_new
    return reponse_token


#This function return refresh token

def retrun_response(statuscd, bodymsg, token):
    auth_response = {
                       'statuscode': statuscd,
                       'body': bodymsg,
                       'accesstoken': token
                    }
    return auth_response
    
    
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