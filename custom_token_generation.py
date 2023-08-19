import jwt
import json
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

gloo_token_raw_data= {
  "token_name": "id_claim",
  "sub": "ae677664-827a-4fa5-b37c-e30abaf9fa30",
  "nbf": 1691521988,
  "iss": "wsdevinternal.usaa.com",
  "expires_in": 600,
  "iat": 1700388461,
  "exp": 1700388461,
  "party_id": "31081",
  "party_type": "USAA",
  "aud": "rsvcint.usaa.com",
  "jti": "c1b20457-cfcf-41d8-92a4-426ebb58f162",
  "token_type": "jwt",
  "realm": "member",
  "groups": [
               "MEMBER"
            ]
}

private_key = b"-----BEGIN PRIVATE KEY-----\nMIGEAgEAMBAGByqGSM49AgEGBS..."
payload_json_str = json.dumps(gloo_token_raw_data)
payload_data = json.loads(payload_json_str)
l=["usaa_resource_server/read_product",
   "usaa_resource_server/create_product",
   "usaa_resource_server/delete_product"
  ]
print('List of values=',l)
payload_new = {"customescope":l, "prefix":"foo_usaa_grp" }
payload_data.update(payload_new)
print('New data payload =',payload_data)
jwt_token_new = jwt.encode(payload_data, private_key, algorithm='HS256', headers={"kid": "230498151c214b788dd97f22b85410a5"},)

#To decode use jwt.decode(encoded, options={"verify_signature": False}) as above function has signed signature
print('Prining new jwt token=',jwt_token_new)