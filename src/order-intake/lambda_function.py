import json
import os
import uuid
from datetime import datetime, timezone
from decimal import Decimal

import boto3


dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["ORDERS_TABLE"])

sqs = boto3.client("sqs")
queue_url = os.environ["ORDER_QUEUE_URL"]


def lambda_handler(event, context):

    try:
        body = json.loads(event.get("body", "{}"))

        customer_id = body.get("customerId")
        items = body.get("items")
        total_amount = body.get("totalAmount")

        if not customer_id or not items or total_amount is None:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "message": "customerId, items and totalAmount are required"
                })
            }

        order_id = str(uuid.uuid4())

        order = {
            "orderId": order_id,
            "customerId": customer_id,
            "items": items,
            "totalAmount": Decimal(str(total_amount)),
            "status": "RECEIVED",
            "createdAt": datetime.now(timezone.utc).isoformat()
        }

        # 1. Store order in DynamoDB
        table.put_item(Item=order)

        # 2. Send order ID to SQS
        message = {
            "orderId": order_id
        }

        sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(message)
        )

        return {
            "statusCode": 202,
            "body": json.dumps({
                "message": "Order accepted for processing",
                "orderId": order_id,
                "status": "RECEIVED"
            })
        }

    except Exception as e:

        print(f"Error processing order: {str(e)}")

        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Internal server error"
            })
        }