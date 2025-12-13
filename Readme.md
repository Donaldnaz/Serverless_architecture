# Serverless Vehicle Rental Backend

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

<img width="976" height="591" alt="Screenshot 2025-12-10 at 3 05 37 PM" src="https://github.com/user-attachments/assets/ed3b3c03-2131-4bca-bfaa-b2502c38e365" />

- Amazon API Gateway for REST API exposure
  <img width="1440" height="727" alt="Screenshot 2025-12-12 at 4 23 25 PM" src="https://github.com/user-attachments/assets/5d18834a-0f13-49f3-8649-4d4a22a04852" />
- AWS Lambda (Python) for stateless business logic
  <img width="1440" height="780" alt="Screenshot 2025-12-12 at 4 02 49 PM" src="https://github.com/user-attachments/assets/d33fe773-9017-45f9-a8f5-55f32cf5b27a" />
- Amazon DynamoDB for high performance NoSQL storage
  <img width="1440" height="726" alt="Screenshot 2025-12-12 at 4 24 05 PM" src="https://github.com/user-attachments/assets/d114c018-4c20-44f4-ade0-7feacdb0376e" />
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

<img width="1440" height="713" alt="Screenshot 2025-12-12 at 3 55 02 PM" src="https://github.com/user-attachments/assets/b85e179a-dbc5-4dbd-a043-294321d92406" />

# Outcome
- Stable and predictable low latency performance
- Automatic scaling during high traffic periods
- Simplified backend operations
- Clean and extensible serverless architecture
