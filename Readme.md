# Event Driven Serverless Application on AWS

## Overview

The goal of the project is to implement a production style event driven application using fully managed AWS services, infrastructure as code, and secure patterns that can scale as traffic grows.

## Architecture

The solution follows a serverless, event driven design:

* Amazon API Gateway exposes public HTTP endpoints for clients
* AWS Lambda functions implement the core business logic in Python
* Amazon DynamoDB stores application data with flexible, low latency access
* Amazon S3 is used for storing payloads, exports, and logs
* Amazon EventBridge or Amazon SQS handles asynchronous events and decoupling
* Amazon CloudWatch provides logging, metrics, and alarms
* AWS IAM controls access between all components
* CloudFormation or AWS SAM defines the full stack as infrastructure as code

This architecture removes the need to manage servers while still supporting high throughput and fault tolerance.

## Features

* REST style API to create, read, and update domain objects  
* Asynchronous processing pipeline for background tasks  
* Idempotent Lambda functions with retry and error handling  
* Centralized logging and metrics for each component  
* Parameterized configuration for different environments such as dev and prod  

## Tech Stack

* AWS API Gateway  
* AWS Lambda  
* Amazon DynamoDB  
* Amazon S3  
* Amazon EventBridge or Amazon SQS  
* Amazon CloudWatch Logs and Metrics  
* AWS IAM  
* CloudFormation/AWS SAM  
* Python  
* Bash for automation scripts  

## Project Structure

Typical layout used in this repo:

* `app.py/` application code for Lambda functions  
* `cloudformation.yaml` infrastructure as code template  
* `requirement.txt` AWS requirements for connection
* `README.md` project documentation  

## How It Works

1. A client sends a request to an API endpoint exposed by API Gateway.  
2. API Gateway forwards the request to the appropriate Lambda function.  
3. The Lambda function validates the input, applies business rules, and writes data to DynamoDB and S3.  
4. For long running or non critical tasks, the function publishes an event to EventBridge or SQS.  
5. Downstream Lambdas subscribe to these events and process them asynchronously.  
6. CloudWatch captures logs, metrics, and alarms for visibility into performance and failures.  

## Getting Started

### Prerequisites

* AWS account  
* IAM user or role with permission to deploy CloudFormation or SAM stacks  
* AWS CLI configured locally  
* Python and pip installed  

### Deployment

- Clone this repository.  
- Install dependencies if a `requirements.txt` file is present.

<img width="1440" height="778" alt="Screenshot 2025-12-09 at 2 51 42 PM" src="https://github.com/user-attachments/assets/fd1b5f93-6fbc-4402-bbb5-417f3294c2ac" />

- Validate the infrastructure template using AWS SAM.

<img width="1440" height="777" alt="Screenshot 2025-12-09 at 3 05 26 PM" src="https://github.com/user-attachments/assets/e77058a0-1610-4ee2-97c2-629919267f54" />

- Deploy the stack using `sam deploy`.
  
- After deployment, copy the API endpoint URL from the stack outputs and test the routes with curl.
  
<img width="1440" height="779" alt="Screenshot 2025-12-09 at 3 12 40 PM" src="https://github.com/user-attachments/assets/3220dae9-e6c9-4d4a-8f0c-b463d69db5cc" />

## Monitoring and Observability

* CloudWatch Logs provide request and error traces for each Lambda function.  
* CloudWatch Metrics track latency, error counts, and throttles.  
* CloudWatch Alarms can be configured to send alerts when thresholds are breached.  

This setup mirrors real world operations practices where you can troubleshoot quickly and understand system behavior over time.

## Security Considerations

* Principle of least privilege applied to IAM roles for Lambda, API Gateway, and other services.  
* Environment variables used for configuration instead of hard coded secrets.  
* Option to integrate AWS KMS for encryption of sensitive values.  
* API Gateway can be secured using IAM auth, Cognito, or API keys depending on the use case.  

## What I Learned

Through this project I reinforced:

* Designing and implementing serverless, event driven architectures on AWS  
* Writing production ready Lambda functions in Python that handle failures gracefully  
* Using infrastructure as code to create repeatable deployments  
* Applying observability and security best practices in a real cloud environment  

## Author
# Anasieze Ikenna - Cloud Engineer
