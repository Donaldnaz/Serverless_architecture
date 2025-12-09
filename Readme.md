# AWS Serverless Architecture – Lambda, API Gateway, DynamoDB & Step Functions.

This repository demonstrates a modular, production-ready AWS Serverless architecture using:

- AWS Lambda
- Amazon API Gateway
- Amazon DynamoDB
- AWS Step Functions
- AWS SAM (Serverless Application Model)
- CloudWatch and X-Ray for observability
- DevOps best practices using CI/CD pipelines

## Technologies Used

| Component       | AWS Service               |
|-----------------|---------------------------|
| Compute         | AWS Lambda                |
| API Gateway     | REST API                  |
| Data Storage    | Amazon DynamoDB           |
| Workflow        | AWS Step Functions        |
| Infrastructure  | AWS SAM (YAML templates)  |
| Observability   | CloudWatch, AWS X-Ray     |
| DevOps          | SAM CLI                   |

## Getting Started

### Prerequisites

- AWS CLI configured (`aws configure`)
- AWS SAM CLI installed
- Node.js 24+ installed

## Features

* Modular Lambda functions
* API Gateway HTTP endpoints
* DynamoDB integration
* Step Functions for orchestration
* Logging and tracing with CloudWatch and X-Ray
* Environment variable support
* DevOps automation with CI/CD pipelines

## Observability
This project includes:

* Structured `console.log()` outputs
* CloudWatch Logs for all Lambda invocations
* AWS X-Ray tracing support (enable in `template.yaml`)


## Author

Created by Anasieze Ikenna - Cloud Engineer


