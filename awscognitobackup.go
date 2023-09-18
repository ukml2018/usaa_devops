// This go code is Taking the backup of cognito
// Author : IBM
package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/cognitoidentityprovider"
)

//func(s int64) *int64 {
//        return &s
//    }

func takeCognitoUserPoolBackup(userPoolID string) error {
	// Create a new AWS session
	sess, err := session.NewSession(&aws.Config{
		Region: aws.String("us-east-1"), // Replace with your desired AWS region
		// Add any other necessary session configuration options
	})
	if err != nil {
		return err
	}

	// Create a new Cognito Identity Provider client
	svc := cognitoidentityprovider.New(sess)

	// Get the user pool details
	describeUserPoolInput := &cognitoidentityprovider.DescribeUserPoolInput{
		UserPoolId: aws.String(userPoolID),
	}
	userPoolData, err := svc.DescribeUserPool(describeUserPoolInput)
	if err != nil {
		return err
	}

	// Get the list of app clients for the user pool
	listUserPoolClientsInput := &cognitoidentityprovider.ListUserPoolClientsInput{
		UserPoolId: aws.String(userPoolID),
	}
	userPoolClients, err := svc.ListUserPoolClients(listUserPoolClientsInput)
	if err != nil {
		return err
	}

	// Get the list of resource servers for the user pool
	f := func(s int64) *int64 {
                return &s
          }
	listResourceServersInput := &cognitoidentityprovider.ListResourceServersInput{
		UserPoolId: aws.String(userPoolID),
		MaxResults: f(10),
	}
	resourceServers, err := svc.ListResourceServers(listResourceServersInput)
	if err != nil {
		return err
	}

	// Get the list of user groups for the user pool
	listGroupsInput := &cognitoidentityprovider.ListGroupsInput{
		UserPoolId: aws.String(userPoolID),
	}
	userGroups, err := svc.ListGroups(listGroupsInput)
	if err != nil {
		return err
	}

	// Get the list of users for the user pool
	listUsersInput := &cognitoidentityprovider.ListUsersInput{
		UserPoolId: aws.String(userPoolID),
	}
	users, err := svc.ListUsers(listUsersInput)
	if err != nil {
		return err
	}

	// Fetch user attributes for each user
	for _, user := range users.Users {
		adminGetUserInput := &cognitoidentityprovider.AdminGetUserInput{
			UserPoolId: aws.String(userPoolID),
			Username:   user.Username,
		}
		userData, err := svc.AdminGetUser(adminGetUserInput)
		if err != nil {
			return err
		}
		user.Attributes = userData.UserAttributes
	}

	// Get the domain details
	describeUserPoolDomainInput := &cognitoidentityprovider.DescribeUserPoolDomainInput{
		Domain:      aws.String(userPoolID),
		//UserPoolId:  aws.String(userPoolID),
	}
	domainConfig, err := svc.DescribeUserPoolDomain(describeUserPoolDomainInput)
	if err != nil {
		return err
	}

	// Create a struct to hold the user pool backup data
	backupData := struct {
		UserPool            *cognitoidentityprovider.UserPoolType               `json:"UserPool"`
		UserPoolClients     []*cognitoidentityprovider.UserPoolClientDescription `json:"UserPoolClients"`
		ResourceServers     []*cognitoidentityprovider.ResourceServerType       `json:"ResourceServers"`
		UserGroups          []*cognitoidentityprovider.GroupType                `json:"UserGroups"`
		Users               []*cognitoidentityprovider.UserType                 `json:"Users"`
		//DomainConfiguration *cognitoidentityprovider.UserPoolDomainDescription  `json:"DomainConfiguration"`
		DomainConfiguration *cognitoidentityprovider.DomainDescriptionType      `json:"DomainConfiguration"`
	}{
		UserPool:            userPoolData.UserPool,
		UserPoolClients:     userPoolClients.UserPoolClients,
		ResourceServers:     resourceServers.ResourceServers,
		UserGroups:          userGroups.Groups,
		Users:               users.Users,
		DomainConfiguration: domainConfig.DomainDescription,
	}

	// Convert the backup data to JSON
	backupJSON, err := json.MarshalIndent(backupData, "", "  ")
	if err != nil {
		return err
	}

	// Write the backup data to a file
	err = ioutil.WriteFile("cognito_user_pool_backup.json", backupJSON, 0644)
	if err != nil {
		return err
	}

	fmt.Println("Cognito user pool backup created successfully.")
	return nil
}

func main() {
	userPoolID := "us-east-1_JvnBSOtpn" // Replace with your actual user pool ID
	err := takeCognitoUserPoolBackup(userPoolID)
	if err != nil {
		fmt.Println("Error taking backup:", err)
		return
	}
}
