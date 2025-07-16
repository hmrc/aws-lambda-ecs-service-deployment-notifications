import json
from typing import TYPE_CHECKING

import boto3

if TYPE_CHECKING:
    from mypy_boto3_lambda.client import LambdaClient
else:
    LambdaClient = object


def get_lambda_client() -> LambdaClient:
    return boto3.client("lambda")


def invoke_lambda(lambda_arn: str, payload: dict) -> None:
    lambda_client = get_lambda_client()
    lambda_client.invoke(
        FunctionName=lambda_arn,
        Payload=json.dumps(payload).encode(),
        InvocationType="Event",
    )


def send_notification(
    lambda_arn: str,
    description: str,
    channel: str,
    cluster_name: str,
    service_name: str,
    reason: str,
    color: str | None = None,
) -> None:
    payload: dict = {
        "channels": [channel],
        "username": "ecs_service_deployment_notifications",
        "text": description,
        "message_content": {
            "fields": [
                {"short": True, "title": "Service Name", "value": service_name},
                {"short": True, "title": "Cluster Name", "value": cluster_name},
                {"short": False, "title": "Reason", "value": reason},
            ]
        },
    }

    if color is not None:
        payload["message_content"]["color"] = color

    invoke_lambda(lambda_arn, payload)
