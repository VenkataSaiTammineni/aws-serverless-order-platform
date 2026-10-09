# AWS Serverless Order Processing Platform

A production-style, event-driven order processing platform built incrementally using AWS managed services and CloudFormation.

The platform demonstrates synchronous API intake, asynchronous order processing, retry handling, dead-letter queues, monitoring, and operational alerting.

---

## Architecture

### Current Architecture — Phases 1–3

```text
                         ┌──────────────────────┐
                         │       Client         │
                         │      / Postman       │
                         └──────────┬───────────┘
                                    │ HTTPS
                                    ▼
                         ┌──────────────────────┐
                         │   API Gateway REST   │
                         │      POST /orders    │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │  Order Intake Lambda │
                         └───────┬────────┬─────┘
                                 │        │
                          PutItem │        │ SendMessage
                                 ▼        ▼
                       ┌──────────────┐  ┌─────────────────┐
                       │  DynamoDB    │  │   SQS Queue     │
                       │    Orders    │  └────────┬────────┘
                       └──────────────┘           │
                                                 ▼
                                      ┌────────────────────┐
                                      │   Worker Lambda    │
                                      └─────────┬──────────┘
                                                │
                                         Get / Update
                                                ▼
                                      ┌────────────────────┐
                                      │     DynamoDB       │
                                      │ RECEIVED →         │
                                      │ PROCESSING →       │
                                      │ COMPLETED          │
                                      └────────────────────┘


                    FAILURE HANDLING
                    ─────────────────

                                      Worker Lambda
                                            │
                                          Failure
                                            ▼
                                        SQS Retry
                                            │
                                  maxReceiveCount = 3
                                            ▼
                                           DLQ
                                            ▼
                                      CloudWatch
                                         Alarm
                                            ▼
                                          SNS
                                            ▼
                                      Email Alert
```

---

# Phase 1 — Serverless Order API

Phase 1 establishes the synchronous order-ingestion layer.

### Flow

```text
Client
   ↓
API Gateway
   ↓
Order Intake Lambda
   ↓
DynamoDB
```

The Order Intake Lambda:

1. Validates the incoming order.
2. Generates a unique `orderId`.
3. Stores the order in DynamoDB.
4. Assigns the initial status `RECEIVED`.
5. Returns the order ID to the client.

### AWS Services

- Amazon API Gateway
- AWS Lambda
- Amazon DynamoDB
- AWS IAM
- Amazon CloudWatch
- AWS CloudFormation

---

# Phase 2 — Asynchronous Order Processing

Phase 2 introduces asynchronous processing using Amazon SQS.

### Flow

```text
Order Intake Lambda
       │
       ├──→ DynamoDB
       │
       └──→ SQS
              │
              ▼
        Worker Lambda
              │
              ▼
          DynamoDB
```

The Order Intake Lambda stores the complete order in DynamoDB and sends only the `orderId` to SQS.

The Worker Lambda:

1. Receives the SQS message.
2. Extracts the `orderId`.
3. Retrieves the order from DynamoDB.
4. Updates the order to `PROCESSING`.
5. Performs the simulated processing.
6. Updates the order to `COMPLETED`.

### Why SQS?

SQS decouples order intake from order processing.

This allows the API to accept orders without waiting for the processing operation to finish.

The API therefore returns:

```text
202 Accepted
```

instead of waiting for the Worker Lambda to complete.

---

# Phase 3 — Failure Handling, DLQ & Monitoring

Phase 3 introduces failure isolation and operational alerting.

### Failure Flow

```text
Worker Lambda
      ↓
    Failure
      ↓
SQS Visibility Timeout
      ↓
     Retry
      ↓
     Retry
      ↓
     Retry
      ↓
     DLQ
      ↓
CloudWatch Alarm
      ↓
     SNS
      ↓
Email Notification
```

The SQS queue is configured with:

- Visibility Timeout: 60 seconds
- Maximum receive count: 3
- Dead Letter Queue enabled

After repeated processing failures, SQS automatically moves the message to the DLQ.

CloudWatch monitors the DLQ and triggers an alarm when messages become visible.

The CloudWatch alarm publishes to an SNS topic, which sends an email notification.

---

# Failure Testing

The failure-handling path was intentionally tested using a controlled failure condition in the Worker Lambda.

The complete failure chain was successfully verified:

```text
Postman
   ↓
API Gateway
   ↓
Order Intake Lambda
   ↓
SQS
   ↓
Worker Lambda
   ↓
Intentional Failure
   ↓
SQS Retries
   ↓
DLQ
   ↓
CloudWatch Alarm
   ↓
SNS
   ↓
Email
```

The Worker was subsequently restored to the normal processing implementation.

---

# Infrastructure as Code

AWS infrastructure is managed using CloudFormation JSON templates.

```text
Infrastructure/
├── Phase-1/
│   ├── OrdersLambda.json
│   ├── api-gateway.json
│   └── dynamodb.json
│
├── Phase-2/
│   ├── sqs.json
│   └── worker-lambda.json
│
└── Phase-3/
    └── monitoring.json
```

CloudFormation exports and imports are used to share resources between stacks.

For example:

```text
DynamoDB Stack
      ↓
    Export
      ↓
Lambda Stack
      ↓
 Fn::ImportValue
```

This keeps infrastructure modular while allowing different CloudFormation stacks to reference shared resources.

---

# Security & IAM

The project follows least-privilege IAM principles.

### Order Intake Lambda

- `dynamodb:PutItem`
- `sqs:SendMessage`
- CloudWatch Logs permissions

### Worker Lambda

- `sqs:ReceiveMessage`
- `sqs:DeleteMessage`
- `sqs:GetQueueAttributes`
- `dynamodb:GetItem`
- `dynamodb:UpdateItem`
- CloudWatch Logs permissions

The Worker Lambda does not have permission to create orders in DynamoDB.

---

# Repository Structure

```text
aws-serverless-order-platform/
│
├── Infrastructure/
│   ├── Phase-1/
│   ├── Phase-2/
│   └── Phase-3/
│
├── src/
│   ├── order-intake/
│   │   └── lambda_function.py
│   │
│   └── order-worker/
│       └── lambda_function.py
│
├── screenshots/
│   └── Phase 2-3/
│
├── docs/
│
├── .gitignore
└── README.md
```

---

# Testing

The system was tested through both successful and failure scenarios.

### Successful Order

```text
RECEIVED
   ↓
PROCESSING
   ↓
COMPLETED
```

### Failed Order

```text
Worker Failure
   ↓
SQS Retry
   ↓
DLQ
   ↓
CloudWatch Alarm
   ↓
SNS Email Alert
```

Testing was performed using:

- Postman
- AWS Lambda test events
- Amazon SQS
- Amazon DynamoDB
- Amazon CloudWatch Logs
- CloudWatch Alarms
- SNS notifications

---

# Evidence

Screenshots demonstrating the implementation and testing are available under:

```text
screenshots/Phase 2-3/
```

Evidence includes:

- CloudFormation stacks
- Successful API request
- Completed DynamoDB order
- SQS queue with DLQ configuration
- Worker Lambda processing
- Worker failure
- CloudWatch DLQ alarm
- SNS email subscription

---

# AWS Services Used

| Service | Purpose |
|---|---|
| API Gateway | REST API entry point |
| Lambda | Order intake and asynchronous processing |
| DynamoDB | Order persistence |
| SQS | Asynchronous message processing |
| SQS DLQ | Failed message isolation |
| CloudWatch | Logs and monitoring |
| SNS | Operational alerting |
| IAM | Least-privilege access control |
| CloudFormation | Infrastructure as Code |

---

# Current Status

### Completed

- [x] Phase 1 — Serverless Order API
- [x] Phase 2 — SQS-based asynchronous processing
- [x] Phase 3 — DLQ, CloudWatch monitoring and SNS alerting
- [x] Failure and retry testing
- [x] CloudFormation infrastructure
- [x] GitHub source control

### Future Roadmap

- [ ] EventBridge event-driven architecture
- [ ] Step Functions workflow orchestration
- [ ] S3 + CloudFront frontend
- [ ] Cognito authentication
- [ ] CI/CD using CodePipeline and CodeBuild
- [ ] Production hardening and observability
- [ ] Cost and reliability optimization

---

## Key Engineering Concepts Demonstrated

- Serverless architecture
- Event-driven architecture
- Asynchronous processing
- Loose coupling
- Message queues
- Retry mechanisms
- Dead Letter Queues
- Failure isolation
- Observability
- Operational alerting
- Infrastructure as Code
- CloudFormation cross-stack dependencies
- IAM least privilege
