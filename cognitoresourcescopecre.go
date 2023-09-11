// This go code is creating new resource group , scopes and attaching scopes with clinet id
// Author : IBM

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
		fmt.Println("Usage: go run main.go <user_pool_id> <resource_server_name> <client_id> <scope_1> <scope_2> ...")
		return
	}

	// Parse command line arguments
	userPoolID := os.Args[1]
	fmt.Println("User Pool ID=",userPoolID)
	resourceServerName := os.Args[2]
	fmt.Println("Resource Server Name=",resourceServerName)
	clientID := os.Args[3]
	fmt.Println("Client ID=",clientID)
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
		return
	}

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
