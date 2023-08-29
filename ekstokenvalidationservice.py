'''
This program will validate the hedaer, signature , expiration time and audiance of the token from EKS
'''

import json
import time
import urllib.request
import boto3
import base64
import hmac
import hashlib
import subprocess
import sys
import os
import datetime
from jose import jwk
from jose.utils import base64url_decode
#from jose import jwk, jwt
#from jose.utils import base64url_decode

#Install pip to install requests
subprocess.check_call([sys.executable, "-m", "pip", "install", "--target", "/tmp", "requests"])

# Add the package to the Python path
sys.path.insert(0, '/tmp')
    
# Import the JWT module
import jwt ,jwk

def base64url_decode(input):
    """Helper method to base64url_decode a string.

    Args:
        input (str): A base64url_encoded string to decode.

    """
    rem = len(input) % 4

    if rem > 0:
        input += b"=" * (4 - rem)

    return base64.urlsafe_b64decode(input)
#region = 'ap-southeast-2'
region = 'us-east-1'
#userpool_id = 'ap-southeast-2_xxxxxxxxx'
userpool_id =  'us-east-1_JvnBSOtpn'
#app_client_id = '<ENTER APP CLIENT ID HERE>'
app_client_id = '3avrvs5l0s3puad6v8vluug2j'
keys_url = 'https://cognito-idp.{}.amazonaws.com/{}/.well-known/jwks.json'.format(region, userpool_id)
print('keys_url=',keys_url)
# instead of re-downloading the public keys every time
# we download them only on cold start
# https://aws.amazon.com/blogs/compute/container-reuse-in-lambda/
with urllib.request.urlopen(keys_url) as f:
  response = f.read()
keys = json.loads(response.decode('utf-8'))['keys']

def lambda_handler(event, context):
    token = event['token']
    # get the kid from the headers prior to verification
    headers = jwt.get_unverified_headers(token)
    kid = headers['kid']
    # search for the kid in the downloaded public keys
    key_index = -1
    for i in range(len(keys)):
        if kid == keys[i]['kid']:
            key_index = i
            break
    if key_index == -1:
        print('Public key not found in jwks.json')
        return False
    # construct the public key
    public_key = jwk.construct(keys[key_index])
    print('Public Key=',public_key)
    # get the last two sections of the token,
    # message and signature (encoded in base64)
    message, encoded_signature = str(token).rsplit('.', 1)
    print('Message=',message)
    print('Message encode=',message.encode("utf8"))
    # decode the signature
    decoded_signature = base64url_decode(encoded_signature.encode('utf-8'))
    print('decoded_signature=',decoded_signature)
    # verify the signature
    if not public_key.verify(message.encode("utf8"), decoded_signature):
        print('Signature verification failed')
        return False
    print('Signature successfully verified')
    # since we passed the verification, we can now safely
    # use the unverified claims
    claims = jwt.get_unverified_claims(token)
    # additionally we can verify the token expiration
    if time.time() > claims['exp']:
        print('Token is expired')
        return False
    # and the Audience  (use claims['client_id'] if verifying an access token)
    if claims['aud'] != app_client_id:
        print('Token was not issued for this audience')
        return False
    # now we can use the claims
    print(claims)
    return claims
        
# the following is useful to make this script executable in both
# AWS Lambda and any other local environments
if __name__ == '__main__':
    # for testing locally you can enter the JWT ID Token here
    event = {'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsImtpZCI6ImxkQVoyRXFyQ0RSZnFWbDcvWUpTd1N2SXkyNlpDRDg4YWlqUUZobkU2ek09In0.eyJ0b2tlbl9uYW1lIjoiaWRfY2xhaW0iLCJzdWIiOiJhZTY3NzY2NC04MjdhLTRmYTUtYjM3Yy1lMzBhYmFmOWZhMzAiLCJuYmYiOjE2OTE1MjE5ODgsImlzcyI6IndzZGV2aW50ZXJuYWwudXNhYS5jb20iLCJleHBpcmVzX2luIjo2MDAsImlhdCI6MTcwMDM4ODQ2MSwiZXhwIjoxNzAwMzg4NDYxLCJwYXJ0eV9pZCI6IjMxMDgxIiwicGFydHlfdHlwZSI6IlVTQUEiLCJhdWQiOiIzYXZydnM1bDBzM3B1YWQ2djh2bHV1ZzJqIiwianRpIjoiYzFiMjA0NTctY2ZjZi00MWQ4LTkyYTQtNDI2ZWJiNThmMTYyIiwidG9rZW5fdHlwZSI6Imp3dCIsInJlYWxtIjoibWVtYmVyIiwiZ3JvdXBzIjpbIk1FTUJFUiJdLCJjbGllbnRfaWQiOiIzYXZydnM1bDBzM3B1YWQ2djh2bHV1ZzJqIiwiY3VzdG9tZXNjb3BlIjpbInVzYWFfcmVzb3VyY2Vfc2VydmVyL3JlYWRfcHJvZHVjdCB1c2FhX3Jlc291cmNlX3NlcnZlci9jcmVhdGVfcHJvZHVjdCB1c2FhX3Jlc291cmNlX3NlcnZlci9kZWxldGVfcHJvZHVjdCJdLCJwcmVmaXgiOiJmb29fdXNhYV9ncnAifQ.HQ7_Qg1XB9u7XKkWg2e-dj-0kRASNLD0YQvi5xSD27Q'}
    lambda_handler(event, None)