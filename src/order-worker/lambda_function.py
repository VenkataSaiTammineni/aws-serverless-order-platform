import json
import os
import boto3


dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["ORDERS_TABLE"])


def lambda_handler(event, context):

    print("Received SQS event:")
    print(json.dumps(event))

    for record in event["Records"]:

        message = json.loads(record["body"])

        order_id = message["orderId"]

        print(f"Processing order: {order_id}")

        # Get the existing order
        response = table.get_item(
            Key={
                "orderId": order_id
            }
        )

        order = response.get("Item")

        if not order:
            print(f"Order not found: {order_id}")
            continue

        # Update status to PROCESSING
        table.update_item(
            Key={
                "orderId": order_id
            },
            UpdateExpression="SET #status = :status",
            ExpressionAttributeNames={
                "#status": "status"
            },
            ExpressionAttributeValues={
                ":status": "PROCESSING"
            }
        )

        print(f"Order {order_id} is now PROCESSING")

        # Simulated processing
        print(f"Processing order {order_id}...")

        # Update status to COMPLETED
        table.update_item(
            Key={
                "orderId": order_id
            },
            UpdateExpression="SET #status = :status",
            ExpressionAttributeNames={
                "#status": "status"
            },
            ExpressionAttributeValues={
                ":status": "COMPLETED"
            }
        )

        print(f"Order {order_id} is now COMPLETED")

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Orders processed successfully"
        })
    }