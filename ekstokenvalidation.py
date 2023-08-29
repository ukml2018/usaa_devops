'''
This script will validate the Cognito Token
Author: Uttam Manna
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
from jose import jwk, jwt
from jose.utils import base64url_decode
#from jose import jwk, jwt
#from jose.utils import base64url_decode

#Install pip to install requests
#subprocess.check_call([sys.executable, "-m", "pip", "install", "--target", "/tmp", "requests"])

# Add the package to the Python path
#sys.path.insert(0, '/tmp')
    
# Import the JWT module
#import jwt 

# total arguments
n = len(sys.argv)
print("Total arguments passed:", n)

# Arguments passed
print("\nName of Python script:", sys.argv[0])

print("\nArguments passed:", end = " ")
for i in range(1, n):
    print(sys.argv[i], end = " ")

token = sys.argv[1]

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
#app_client_id = '3avrvs5l0s3puad6v8vluug2j'
keys_url = 'https://cognito-idp.{}.amazonaws.com/{}/.well-known/jwks.json'.format(region, userpool_id)
print('keys_url=',keys_url)
# instead of re-downloading the public keys every time
# we download them only on cold start
# https://aws.amazon.com/blogs/compute/container-reuse-in-lambda/
with urllib.request.urlopen(keys_url) as f:
  response = f.read()
keys = json.loads(response.decode('utf-8'))['keys']
print('keys=',keys)
def lambda_handler(event, context):
    token = event['token']
    app_client = jwt.get_unverified_claims(token)
    app_client_id = app_client['client_id']
    print('App Client Id=',app_client_id)
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
    #print('Public Key=',public_key)
    # get the last two sections of the token,
    # message and signature (encoded in base64)
    message, encoded_signature = str(token).rsplit('.', 1)
    #print('Message=',message)
    #print('Message encode=',message.encode("utf8"))
    # decode the signature
    decoded_signature = base64url_decode(encoded_signature.encode('utf-8'))
    #print('decoded_signature=',decoded_signature)
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
    #if claims['aud'] != app_client_id:
    if claims['client_id'] != app_client_id:   
        print('Token was not issued for this audience')
        return False
    # now we can use the claims
    print(claims)
    return claims
        
# the following is useful to make this script executable in both
# AWS Lambda and any other local environments
if __name__ == '__main__':
    # for testing locally you can enter the JWT ID Token here
    event = {'token':token}
    lambda_handler(event, None)
