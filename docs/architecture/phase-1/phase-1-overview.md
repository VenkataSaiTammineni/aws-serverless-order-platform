# Phase 1 — Serverless Order API

## Objective

Build the first working version of the AWS Serverless Order Processing Platform.

The Phase 1 architecture accepts an order through an API Gateway REST API, processes the request using AWS Lambda, and stores the order in Amazon DynamoDB.

## Architecture

Client
↓
Amazon API Gateway REST API
↓
AWS Lambda — Order Intake
↓
Amazon DynamoDB — Orders

## AWS Services

- Amazon API Gateway
- AWS Lambda
- Amazon DynamoDB
- AWS IAM
- Amazon CloudWatch
- AWS CloudFormation

## Region

AWS Region:

`ap-south-1` — Mumbai

## Infrastructure as Code

All Phase 1 infrastructure is managed using AWS CloudFormation JSON templates.

Templates:

- `infrastructure/phase-1/dynamodb.json`
- `infrastructure/phase-1/lambda.json`
- `infrastructure/phase-1/api-gateway.json`

## DynamoDB

Table:

`order-platform-orders`

Partition Key:

`orderId`

Type:

`String`

## Lambda

Function:

`order-platform-order-intake`

Runtime:

Python

Responsibilities:

- Receive order requests
- Validate required fields
- Generate unique order IDs
- Generate timestamps
- Set initial order status
- Store orders in DynamoDB
- Return an HTTP response

Initial order status:

`RECEIVED`

## API

Endpoint:

`POST /orders`

Example request:

```json
{
  "customerId": "CUST-001",
  "items": [
    {
      "productId": "P-100",
      "quantity": 2
    }
  ],
  "totalAmount": 300.00
}
