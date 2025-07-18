import dataclasses
import os
import unittest.mock

import pytest
from ecs_service_deployment_notifications.handler import handler


@pytest.mark.parametrize(
    "event",
    [
        pytest.param(
            {
                "resources": [],
            },
            id="no_detail",
        ),
        pytest.param(
            {
                "resources": [],
                "detail": {
                    "reason": "No reason",
                },
            },
            id="no_event_name",
        ),
    ],
)
def test_handler_raises_exception_on_missing_event_name(event):
    context = {}

    with pytest.raises(ValueError) as exc_info:
        handler(event, context)

    assert str(exc_info.value) == "Missing event name"


def test_handler_raises_exception_on_unexpected_event_name():
    context = {}

    with pytest.raises(ValueError) as exc_info:
        handler(
            {
                "resources": [],
                "detail": {
                    "eventName": "NOT_A_SERVICE_DEPLOYMENT",
                    "reason": "No reason",
                },
            },
            context,
        )

    assert str(exc_info.value) == "Unexpected event name NOT_A_SERVICE_DEPLOYMENT"


@dataclasses.dataclass
class MockServiceArn:
    cluster_name: str
    service_name: str


@unittest.mock.patch("ecs_service_deployment_notifications.slack.send_notification")
@unittest.mock.patch("ecs_service_deployment_notifications.ecs.ServiceArn")
def test_handler_sends_notification_for_configured_cluster(
    mock_service_arn: unittest.mock.MagicMock,
    mock_send_notification: unittest.mock.MagicMock,
):
    cluster_name = "notified-cluster-name"
    service_name = "service-name"
    slack_channel = "test-channel"
    lambda_arn = "arn:aws:lambda:eu-west-2:123456789012:function:example-function:1"

    event = {
        "resources": [f"arn:MOCKED:service/{cluster_name}/{service_name}"],
        "detail": {
            "eventName": "SERVICE_DEPLOYMENT_IN_PROGRESS",
            "reason": "No reason",
        },
    }
    context = {}

    mock_service_arn.return_value = MockServiceArn(cluster_name=cluster_name, service_name=service_name)

    with unittest.mock.patch.dict(
        os.environ,
        {
            "CLUSTER_NAME": cluster_name,
            "SLACK_CHANNEL": slack_channel,
            "SLACK_NOTIFICATIONS_LAMBDA_ARN": lambda_arn,
        },
        clear=True,
    ):
        handler(event, context)

    mock_send_notification.assert_called_once_with(
        lambda_arn=lambda_arn,
        description="ECS service deployment in progress",
        color=None,
        channel=slack_channel,
        cluster_name=cluster_name,
        service_name=service_name,
        reason="No reason",
    )


@unittest.mock.patch("ecs_service_deployment_notifications.slack.send_notification")
@unittest.mock.patch("ecs_service_deployment_notifications.ecs.ServiceArn")
def test_handler_does_not_send_notification_for_other_clusters(
    mock_service_arn: unittest.mock.MagicMock,
    mock_send_notification: unittest.mock.MagicMock,
):
    event = {
        "resources": ["arn:MOCKED:service/unnotified-cluster-name/service-name"],
        "detail": {
            "eventName": "SERVICE_DEPLOYMENT_IN_PROGRESS",
            "reason": "No reason",
        },
    }
    context = {}

    mock_service_arn.return_value = MockServiceArn(cluster_name="unnotified-cluster-name", service_name="service-name")

    with unittest.mock.patch.dict(
        os.environ,
        {
            "CLUSTER_NAME": "notified-cluster-name",
            "SLACK_CHANNEL": "test-channel",
            "SLACK_NOTIFICATIONS_LAMBDA_ARN": "test-arn",
        },
        clear=True,
    ):
        handler(event, context)

    mock_send_notification.assert_not_called()


@unittest.mock.patch("ecs_service_deployment_notifications.slack.send_notification")
@unittest.mock.patch("ecs_service_deployment_notifications.ecs.ServiceArn")
def test_handler_sends_notification_for_each_resource(
    mock_service_arn: unittest.mock.MagicMock,
    mock_send_notification: unittest.mock.MagicMock,
):
    cluster_name = "notified-cluster-name"
    service_name = "service-name"
    slack_channel = "test-channel"
    lambda_arn = "arn:aws:lambda:eu-west-2:123456789012:function:example-function:1"

    event = {
        "resources": [
            f"arn:MOCKED:service/{cluster_name}/{service_name}-1",
            f"arn:MOCKED:service/{cluster_name}/{service_name}-2",
        ],
        "detail": {
            "eventName": "SERVICE_DEPLOYMENT_IN_PROGRESS",
            "reason": "No reason",
        },
    }
    context = {}

    mock_service_arn.side_effect = [
        MockServiceArn(cluster_name=cluster_name, service_name=f"{service_name}-1"),
        MockServiceArn(cluster_name=cluster_name, service_name=f"{service_name}-2"),
    ]

    with unittest.mock.patch.dict(
        os.environ,
        {
            "CLUSTER_NAME": cluster_name,
            "SLACK_CHANNEL": slack_channel,
            "SLACK_NOTIFICATIONS_LAMBDA_ARN": lambda_arn,
        },
        clear=True,
    ):
        handler(event, context)

    assert mock_send_notification.call_args_list == [
        unittest.mock.call(
            lambda_arn=lambda_arn,
            description="ECS service deployment in progress",
            color=None,
            channel=slack_channel,
            cluster_name=cluster_name,
            service_name=f"{service_name}-1",
            reason="No reason",
        ),
        unittest.mock.call(
            lambda_arn=lambda_arn,
            description="ECS service deployment in progress",
            color=None,
            channel=slack_channel,
            cluster_name=cluster_name,
            service_name=f"{service_name}-2",
            reason="No reason",
        ),
    ]
