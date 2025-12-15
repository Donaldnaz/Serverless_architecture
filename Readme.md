# Serverless: Solving Performance Issues with API Gateway, Lambda and DynamoDB

This repository contains a serverless backend system designed to modernize a vehicle rental platform that previously relied on a relational SQL database. The solution is built on AWS managed services to support unpredictable traffic spikes while maintaining consistent low latency performance.

---

## Project Overview

The legacy backend experienced performance issues during peak demand periods due to database contention and scaling limitations. To resolve this, the backend was redesigned using a serverless and NoSQL-first approach.

The primary goals of this project were:

- Consistent millisecond response times under load
- Automatic scaling during traffic surges
- Removal of database connection bottlenecks
- Reduced operational and infrastructure overhead

## Architecture

The backend uses the following AWS services:

- Amazon API Gateway for REST API exposure
- AWS Lambda (Python) for stateless business logic
- Amazon DynamoDB for high performance NoSQL storage
- Amazon CloudWatch for logging, metrics, and monitoring

### Request Flow

1. A client sends a request to an API Gateway endpoint
3. API Gateway routes the request to a Lambda function  
4. Lambda executes application logic and interacts with DynamoDB  
5. CloudWatch captures logs and performance metrics  

## Data Model

A single-table DynamoDB design is used to ensure predictable performance and scalability.

**Table Name:** rental_app

**Partition Key:** record_type
**Sort Key:** id

# Outcome
- Stable and predictable low latency performance
- Automatic scaling during high traffic periods
- Simplified backend operations
- Clean and extensible serverless architecture
