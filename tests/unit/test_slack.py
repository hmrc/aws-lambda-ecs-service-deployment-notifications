import unittest.mock

import boto3
import botocore.stub
import ecs_service_deployment_notifications.slack as slack
import pytest


@pytest.fixture
def stubbed_lambda_client():
    client = boto3.client("lambda", region_name="eu-west-2")

    with unittest.mock.patch("ecs_service_deployment_notifications.slack.get_lambda_client") as mock_get_lambda_client:
        mock_get_lambda_client.return_value = client
        yield client


@pytest.fixture
def lambda_client_stubber(stubbed_lambda_client):
    return botocore.stub.Stubber(stubbed_lambda_client)


def test_invoke_lambda(lambda_client_stubber: botocore.stub.Stubber):
    lambda_arn = "arn:aws:lambda:eu-west-2:123456789012:function:example-function:1"

    lambda_client_stubber.add_response(
        method="invoke",
        service_response={"StatusCode": 200},
        expected_params=dict(
            FunctionName=lambda_arn,
            InvocationType="Event",
            Payload=b'{"text": "hoooray!"}',
        ),
    )

    with lambda_client_stubber:
        slack.invoke_lambda(lambda_arn, {"text": "hoooray!"})

    lambda_client_stubber.assert_no_pending_responses()


@unittest.mock.patch("ecs_service_deployment_notifications.slack.invoke_lambda")
def test_send_notification_with_color(mock_invoke_lambda: unittest.mock.MagicMock):
    lambda_arn = "arn:aws:lambda:eu-west-2:123456789012:function:example-function:1"
    description = "ECS service deployment in progress"
    color = "good"
    channel = "event-integ-recycle"
    cluster_name = "cluster-name"
    service_name = "service-name"
    reason = "No reason, just felt like it"

    slack.send_notification(
        lambda_arn=lambda_arn,
        description=description,
        color=color,
        channel=channel,
        cluster_name=cluster_name,
        service_name=service_name,
        reason=reason,
    )

    mock_invoke_lambda.assert_called_once_with(
        lambda_arn,
        {
            "channels": [channel],
            "username": "ecs_service_deployment_notifications",
            "text": description,
            "message_content": {
                "color": color,
                "fields": [
                    {"short": True, "title": "Service Name", "value": service_name},
                    {"short": True, "title": "Cluster Name", "value": cluster_name},
                    {"short": False, "title": "Reason", "value": reason},
                ],
            },
        },
    )


@unittest.mock.patch("ecs_service_deployment_notifications.slack.invoke_lambda")
def test_send_notification_without_color(mock_invoke_lambda: unittest.mock.MagicMock):
    lambda_arn = "arn:aws:lambda:eu-west-2:123456789012:function:example-function:1"
    description = "ECS service deployment in progress"
    channel = "event-integ-recycle"
    cluster_name = "cluster-name"
    service_name = "service-name"
    reason = "No reason, just felt like it"

    slack.send_notification(
        lambda_arn=lambda_arn,
        description=description,
        channel=channel,
        cluster_name=cluster_name,
        service_name=service_name,
        reason=reason,
    )

    mock_invoke_lambda.assert_called_once_with(
        lambda_arn,
        {
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
        },
    )
