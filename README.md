# AWS-EC2_S3_interactions_Boto3_Python3
Program that lets you interact with EC2 and S3 using Boto3 through a user-friendly CLI. A personal project of mine.

This a personal project of mine and below is the project design documentation

--------------------------------------------Project Design Documentation--------------------------------------------

--Introduction--
  - For this project I am aiming to a build a basic replication of the AWS console but only for EC2 and S3 services using python3 and boto3.
    I will build a user-friendly CLI that lets users interact with AWS EC2 and S3 services such launching an EC2 instance or pulling a list of your S3 buckets 
    but with far less granularity when interacting with these services.


--Requirements --
  - There will be user-friendly CLI for the user to interact with and from here, user should be able to pass arguments and values that should perform tasks like listing ec2 instances or s3 buckets, change instance state, or upload or delete buckets and objects.  Users, however, will have to first pass their username before being allowed to take any actions. User actions will also be logged to an S3 bucket


--System Interactions--
  - User friendly CLI will be created with the help of argparser module. 
  - User requests which are passed as arguments will be handled with boto3 functions
  - These boto3 functions and code will talk directly to the AWS service by utilizing its service API and creating a console session with the service(S3, EC2, etc.)
  - IF statements will be implemented that will invoke functions based on arguments passed
  - Users will be created and stored in a DynamoDB table
  - User actions will be logged through the use of the logging module. File to store the logs will be created upon running the script and then uploaded to S3
 
 Full design doc - https://docs.google.com/document/d/1BzujbQoAxJ250XQqIZ0QFLyTDHzb61wCTn9MLx82VxE/edit?usp=sharing
