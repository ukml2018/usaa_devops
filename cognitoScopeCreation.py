'''
This function will create resource server and custom scopes dynamically
Author: IBM
'''
import boto3

def create_resource_server(user_pool_id, identifier, name, scopes):
    client = boto3.client('cognito-idp')

    response = client.create_resource_server(
        UserPoolId=user_pool_id,
        Identifier=identifier,
        Name=name,
        Scopes=scopes
    )

    print(f"Resource server created successfully: {response['ResourceServer']['Identifier']}")

def create_custom_scopes(user_pool_id, resource_server_id, scopes):
    client = boto3.client('cognito-idp')

    for scope in scopes:
        response = client.create_resource_server_scope(
            UserPoolId=user_pool_id,
            #Identifier=scope['identifier'],
            Identifier=resource_server_id,
            Name=scope['name'],
            ResourceServerIdentifier=resource_server_id
        )

        print(f"Custom scope created successfully: {response['Scope']['Identifier']}")

# Example usage
if __name__ == '__main__':
    # Set your AWS region and user pool ID
    region = 'us-east-1'
    user_pool_id = 'us-east-1_JvnBSOtpn'

    # Create a resource server
    resource_server_identifier = 'my-resource-server1'
    resource_server_name = 'My Resource Server'
    create_resource_server(user_pool_id, resource_server_identifier, resource_server_name, [])

    # Create custom scopes
    custom_scopes = [
        {
            'identifier': 'scope1',
            'name': 'Scope 1'
        },
        {
            'identifier': 'scope2',
            'name': 'Scope 2'
        }
    ]
    create_custom_scopes(user_pool_id, resource_server_identifier, custom_scopes)