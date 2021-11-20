# AWS-EC2_S3_interactions_Boto3_Python3
Program that lets you interact with EC2 and S3 using Boto3 through a user-friendly CLI. A personal project of mine.

This a personal project of mine and below is the project design documentation

--------------------------------------------------------------------Project Design Documentation------------------------------------------------------------------------------

--Introduction--
  - For this project I am aiming to a build a basic replication of the AWS console but only for EC2 and S3 services using python3 and boto3.
    I will build a user-friendly CLI that lets users interact with AWS EC2 and S3 services such launching an EC2 instance or pulling a list of your S3 buckets 
    but with far less granularity when interacting with these services.


--Requirements --
  - There will be user-friendly CLI for the user to interact with and from here, user should be able to pass arguments and values that should perform tasks like 
    listing ec2 instances or s3 buckets, change instance state, or upload or delete buckets and objects.
  - With a user-friendly CLI, users should be presented with options/arguments that lets them perform various S3 and EC2 actions


--System Interactions--
  - User friendly CLI will be created with the help of argparser module. 
  - User requests which are passed as arguments will be handled with boto3 functions
  - These boto3 functions and code will talk directly to the AWS service by utilizing its service API and creating a console session with the service(S3, EC2, etc.)
  - IF statements will be implemented that will invoke functions based on arguments passed 


--Implementation Details-- 
  - Program Features
      o	User-friendly CLI
      o	Actions
          - EC2
              •	Launch EC2 instances
              •	List EC2 instances
              •	Change the state of instances (stop, start, terminate)
          - S3
              •	Create buckets
              •	List buckets 
              •	Delete bucket
              •	Upload objects
              •	Download objects
              •	List objects
              •	Delete objects
              
  - User-Friendly Command Line Interface 
      o	The argparse module will be used to build the CLI.
      o	User will be able to interact with the program by passing arguments to the python script
      o	The --help arguments can be passed which will provide detailed information of how to use the program
      o	Passed arguments will be parsed then passed to boto3 functions to handle user request
  
  - Launch, list and change the state of instances
      o	Program will provide two ways to launch instances
          - User can simply launch one or more free tire instances with predefined specifications  by passing the --create argument with the number of instances to launch
          - If user wants to provide specifications for the instances, instead of passing the number of instances to be launch to the --create argument, user can instead pass 
          the word "custom" to the --create argument. User will be taken through a series of prompts where they can enter some specifications for the instance
      o	User can pass the --list argument to list all the instances on the account and their state. 
          - In addition to passing the --list argument, user can also pass the -id argument with the id of the instance to see more information about specific instance 
      o	When changing instance state, user will the option to apply state change to all of their existing instances or to a specific instance
          - To change the state of all existing instances, simply pass the --state argument with the state option (stop, start, or terminate)
          - To change the state of a specific instance, along with passing the --state argument with the state option, the -id argument with the id of the instance must also be passed
 
 - Create, modify, and upload to S3 buckets
      o	For creating a bucket, the -cb argument will be passed with a name for the bucket
      o	To list existing buckets, pass the -lb argument
      o	To delete bucket, pass the --delbkt argument with the name of the bucket to delete
      o	To list objects in a buckets, pass the -lo argument with the name of the bucket
      o	To upload file/object to a bucket, pass the --upload argument with the file path and the bucket name
      o	To download file/object from a bucket, pass the --download argument with the file name and the bucket name, and the path for the file to be stored
      o	To delete an object/file for a bucket, pass the --delobj arguments with the file name and the bucket name.