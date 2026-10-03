# AWS Serverless Order Processing Platform

A production-style serverless order-processing platform built incrementally using AWS services and CloudFormation.

## Phase 1 — Serverless Order API

### Architecture

Client
↓
Amazon API Gateway REST API
↓
AWS Lambda
↓
Amazon DynamoDB

### AWS Services

- Amazon API Gateway
- AWS Lambda
- Amazon DynamoDB
- AWS IAM
- Amazon CloudWatch
- AWS CloudFormation

### Infrastructure as Code

AWS infrastructure is managed using CloudFormation JSON templates.

```text
infrastructure/
└── phase-1/
    ├── dynamodb.json
    ├── lambda.json
    └── api-gateway.json