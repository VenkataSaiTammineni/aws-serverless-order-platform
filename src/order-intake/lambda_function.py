import json
import os
import uuid
from datetime import datetime, timezone
from decimal import Decimal

import boto3


dynamodb = boto3.resource("dynamodb")

table = dynamodb.Table(
    os.environ["ORDERS_TABLE"]
)


def lambda_handler(event, context):

    print("Received event:")
    print(json.dumps(event))

    try:
        body = json.loads(
            event.get("body", "{}")
        )

        customer_id = body.get("customerId")
        items = body.get("items")
        total_amount = body.get("totalAmount")

        if not customer_id or not items or total_amount is None:

            return {
                "statusCode": 400,
                "headers": {
                    "Content-Type": "application/json"
                },
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
            "createdAt": datetime.now(
                timezone.utc
            ).isoformat()
        }

        table.put_item(Item=order)

        print(
            f"Order created successfully: {order_id}"
        )

        return {
            "statusCode": 201,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "message": "Order created successfully",
                "orderId": order_id,
                "status": "RECEIVED"
            })
        }

    except Exception as e:

        print(
            f"Error processing order: {str(e)}"
        )

        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "message": "Internal server error"
            })
        }