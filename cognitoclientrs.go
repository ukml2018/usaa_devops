// This go code is creating new resource group , scopes, App client  and attaching scopes with clinet id
// Author : Uttam Manna  Date: 11-09-2023 

package main

import (
	"fmt"
	"os"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/cognitoidentityprovider"
)

func main() {
	// Check if the required command line arguments are provided
	if len(os.Args) < 5 {
		fmt.Println("Usage: go run main.go <user_pool_id> <resource_server_name> <client_name>  <scope_1> <scope_2> ...")
		return
	}

	// Parse command line arguments
	userPoolID := os.Args[1]
	fmt.Println("User Pool ID=",userPoolID)
	resourceServerName := os.Args[2]
	fmt.Println("Resource Server Name=",resourceServerName)
	clientName := os.Args[3]
	fmt.Println("Client Name=",clientName)
	scopes := os.Args[4:]
        //scopes1 := []string{scopes}

	// Preparing scopes for cognito app client
        AllowedOAuthScopesGen := []string{}
        for _, scope := range scopes{
            AllowedOAuthScopesGen = append(AllowedOAuthScopesGen, resourceServerName+"/"+scope)
        } 
	// Create a new AWS session
	sess, err := session.NewSession(&aws.Config{
		Region: aws.String("us-east-1"), // Replace with your desired region
	})
	if err != nil {
		fmt.Println("Failed to create session:", err)
		return
	}

	// Create a new AWS Cognito Identity Provider client
	cognitoClient := cognitoidentityprovider.New(sess)

	// Create the resource server scopes
	resourceServerScopes := make([]*cognitoidentityprovider.ResourceServerScopeType, len(scopes))
	for i, scope := range scopes {
		resourceServerScopes[i] = &cognitoidentityprovider.ResourceServerScopeType{
			ScopeName:        aws.String(scope),
			ScopeDescription: aws.String(fmt.Sprintf("Access to %s", scope)),
		}
	}
     
	// Create the resource server
	createInput := &cognitoidentityprovider.CreateResourceServerInput{
		Identifier:   aws.String(resourceServerName),
		Name:         aws.String(resourceServerName),
		Scopes:       resourceServerScopes,
		UserPoolId:   aws.String(userPoolID),
	}
	_, err = cognitoClient.CreateResourceServer(createInput)
	if err != nil {
		fmt.Println("Failed to create resource server:", err)
		//return
	}


	// Create the Cognito client
	/*
	createInput1 := &cognitoidentityprovider.CreateUserPoolClientInput{
		UserPoolId: aws.String(userPoolID),
		ClientName: aws.String(clientName),
		CallbackURLs: []*string{
			//aws.String(callbackURL),
			aws.String("https://www.google.com"),
		},
		AllowedOAuthFlows: []*string{
			aws.String("code"),
		},
		AllowedOAuthScopes: []*string{
			aws.String("openid"),
			aws.String("email"),
		},
	}
	*/
        	
	createInput1 := &cognitoidentityprovider.CreateUserPoolClientInput{
		UserPoolId: aws.String(userPoolID),
		ClientName: aws.String(clientName),
		GenerateSecret: aws.Bool(true),
		AllowedOAuthFlows: []*string{
			aws.String("client_credentials"),
		},
		//AllowedOAuthScopes: aws.StringSlice(scopes),
		AllowedOAuthScopes: aws.StringSlice(AllowedOAuthScopesGen),
	}
        	
	result, err := cognitoClient.CreateUserPoolClient(createInput1)
	if err != nil {
		fmt.Println("Failed to create Cognito client:", err)
		//return
	}
     
	// Print the client ID and client secret
	fmt.Println("Cognito client created successfully.")
	fmt.Println("Client ID:", *result.UserPoolClient.ClientId)
	fmt.Println("Client Secret:", *result.UserPoolClient.ClientSecret)

        // List all the Cognito clients in the User Pool
	listInput1 := &cognitoidentityprovider.ListUserPoolClientsInput{
		UserPoolId: aws.String(userPoolID),
	}
	result1, err := cognitoClient.ListUserPoolClients(listInput1)
	if err != nil {
		fmt.Println("Failed to list Cognito clients:", err)
		return
	}

	// Find the client ID based on the client name
	var clientID string
	for _, client := range result1.UserPoolClients {
        //for _, client := range result1.ListUserPoolClients{	
	       if *client.ClientName == clientName {
			clientID = *client.ClientId
			break
		}
	}

	if clientID == "" {
		fmt.Printf("Cognito client '%s' not found\n", clientName)
		return
	}

	// Print the client ID
	fmt.Println("Cognito client found.")
	fmt.Println("Client ID:", clientID)

	// Attach scopes to the client ID
	attachInput := &cognitoidentityprovider.UpdateUserPoolClientInput{
		UserPoolId: aws.String(userPoolID),
		ClientId:   aws.String(clientID),
	        SupportedIdentityProviders: []*string{
		        aws.String("COGNITO"), // Replace with other supported identity providers if needed
		},
		AllowedOAuthFlows: []*string{
			aws.String("client_credentials"),
		},
		CallbackURLs:  []*string{aws.String("https://www.google.com")},
		AllowedOAuthFlowsUserPoolClient: aws.Bool(true),
		AllowedOAuthScopes: aws.StringSlice(AllowedOAuthScopesGen),
		//AllowedOAuthScopes: resourceServerScopes,
		//AllowedOAuthScopes: []*string{
		//	aws.String(scopes),
		//},	
	}
	_, err = cognitoClient.UpdateUserPoolClient(attachInput)
	if err != nil {
		fmt.Println("Failed to attach scopes to client:", err)
		return
	}

	fmt.Println("Resource server created and scopes attached successfully.")
}
