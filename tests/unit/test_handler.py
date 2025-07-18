import dataclasses
import json
import logging
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
def test_handler_raises_exception_on_missing_event_name(event: dict):
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
    arn: str
    cluster_name: str
    service_name: str


@unittest.mock.patch("ecs_service_deployment_notifications.slack.send_notification")
@unittest.mock.patch("ecs_service_deployment_notifications.ecs.ServiceArn")
def test_handler_sends_notification_for_configured_cluster(
    mock_service_arn: unittest.mock.MagicMock,
    mock_send_notification: unittest.mock.MagicMock,
):
    service_arn = "arn:test"
    cluster_name = "cluster-name"
    service_name = "service-name"
    slack_channel = "test-channel"
    lambda_arn = "arn:aws:lambda:eu-west-2:123456789012:function:example-function:1"

    event = {
        "resources": [service_arn],
        "detail": {
            "eventName": "SERVICE_DEPLOYMENT_IN_PROGRESS",
            "reason": "No reason",
        },
    }
    context = {}

    mock_service_arn.return_value = MockServiceArn(
        arn=service_arn, cluster_name=cluster_name, service_name=service_name
    )

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
    service_arn = "arn:test"
    cluster_name = "cluster-name"
    service_name = "service-name"
    slack_channel = "test-channel"
    lambda_arn = "arn:aws:lambda:eu-west-2:123456789012:function:example-function:1"

    event = {
        "resources": [service_arn],
        "detail": {
            "eventName": "SERVICE_DEPLOYMENT_IN_PROGRESS",
            "reason": "No reason",
        },
    }
    context = {}

    mock_service_arn.return_value = MockServiceArn(
        arn=service_arn, cluster_name=cluster_name, service_name=service_name
    )

    with unittest.mock.patch.dict(
        os.environ,
        {
            "CLUSTER_NAME": f"not-{cluster_name}",
            "SLACK_CHANNEL": slack_channel,
            "SLACK_NOTIFICATIONS_LAMBDA_ARN": lambda_arn,
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
    service_arn = "arn:test"
    cluster_name = "cluster-name"
    service_name = "service-name"
    slack_channel = "test-channel"
    lambda_arn = "arn:aws:lambda:eu-west-2:123456789012:function:example-function:1"

    event = {
        "resources": [
            f"{service_arn}-1",
            f"{service_arn}-2",
        ],
        "detail": {
            "eventName": "SERVICE_DEPLOYMENT_IN_PROGRESS",
            "reason": "No reason",
        },
    }
    context = {}

    mock_service_arn.side_effect = [
        MockServiceArn(arn=f"{service_arn}-1", cluster_name=cluster_name, service_name=f"{service_name}-1"),
        MockServiceArn(arn=f"{service_arn}-2", cluster_name=cluster_name, service_name=f"{service_name}-2"),
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


@unittest.mock.patch("ecs_service_deployment_notifications.slack.send_notification")
@unittest.mock.patch("ecs_service_deployment_notifications.ecs.ServiceArn")
def test_handler_logs_at_info_on_sending_notifications(
    mock_service_arn: unittest.mock.MagicMock,
    mock_send_notification: unittest.mock.MagicMock,
    caplog: pytest.LogCaptureFixture,
):
    service_arn = "arn:test"
    cluster_name = "cluster-name"
    service_name = "service-name"
    slack_channel = "test-channel"
    lambda_arn = "arn:aws:lambda:eu-west-2:123456789012:function:example-function:1"

    event = {
        "resources": [
            f"{service_arn}-1",
            f"{service_arn}-2",
        ],
        "detail": {
            "eventName": "SERVICE_DEPLOYMENT_IN_PROGRESS",
            "reason": "No reason",
        },
    }
    context = {}

    mock_service_arn.side_effect = [
        MockServiceArn(arn=f"{service_arn}-1", cluster_name=cluster_name, service_name=f"{service_name}-1"),
        MockServiceArn(arn=f"{service_arn}-2", cluster_name=cluster_name, service_name=f"{service_name}-2"),
    ]

    with unittest.mock.patch.dict(
        os.environ,
        {
            "CLUSTER_NAME": cluster_name,
            "SLACK_CHANNEL": slack_channel,
            "SLACK_NOTIFICATIONS_LAMBDA_ARN": lambda_arn,
            "LOG_LEVEL": "INFO",
        },
        clear=True,
    ):
        handler(event, context)

    assert caplog.record_tuples == [
        (
            "root",
            logging.INFO,
            f"Sending SERVICE_DEPLOYMENT_IN_PROGRESS notification for {service_arn}-1",
        ),
        (
            "root",
            logging.INFO,
            f"Sending SERVICE_DEPLOYMENT_IN_PROGRESS notification for {service_arn}-2",
        ),
    ]


@pytest.mark.parametrize("log_level", ["DEBUG", "INFO", "WARN", "ERROR"])
@unittest.mock.patch("logging.getLogger")
def test_handler_sets_log_level_from_environment(mock_get_logger: unittest.mock.MagicMock, log_level: str):
    cluster_name = "cluster-name"
    slack_channel = "test-channel"
    lambda_arn = "arn:aws:lambda:eu-west-2:123456789012:function:example-function:1"

    event = {
        "resources": [],
        "detail": {
            "eventName": "SERVICE_DEPLOYMENT_COMPLETED",
            "reason": "No reason",
        },
    }
    context = {}

    mock_logger = unittest.mock.MagicMock()
    mock_get_logger.return_value = mock_logger

    with unittest.mock.patch.dict(
        os.environ,
        {
            "CLUSTER_NAME": cluster_name,
            "SLACK_CHANNEL": slack_channel,
            "SLACK_NOTIFICATIONS_LAMBDA_ARN": lambda_arn,
            "LOG_LEVEL": log_level,
        },
        clear=True,
    ):
        handler(event, context)

    mock_logger.setLevel.assert_called_once_with(log_level)


@unittest.mock.patch("ecs_service_deployment_notifications.slack.send_notification")
@unittest.mock.patch("ecs_service_deployment_notifications.ecs.ServiceArn")
def test_handler_logs_event_at_debug(
    mock_service_arn: unittest.mock.MagicMock,
    mock_send_notification: unittest.mock.MagicMock,
    caplog: pytest.LogCaptureFixture,
):
    cluster_name = "cluster-name"
    slack_channel = "test-channel"
    lambda_arn = "arn:aws:lambda:eu-west-2:123456789012:function:example-function:1"

    event = {
        "resources": [],
        "detail": {
            "eventName": "SERVICE_DEPLOYMENT_COMPLETED",
            "reason": "No reason",
        },
    }
    context = {}

    with unittest.mock.patch.dict(
        os.environ,
        {
            "CLUSTER_NAME": cluster_name,
            "SLACK_CHANNEL": slack_channel,
            "SLACK_NOTIFICATIONS_LAMBDA_ARN": lambda_arn,
            "LOG_LEVEL": "DEBUG",
        },
        clear=True,
    ):
        handler(event, context)

    assert ("root", logging.DEBUG, json.dumps(event)) in caplog.record_tuples


@unittest.mock.patch("ecs_service_deployment_notifications.slack.send_notification")
@unittest.mock.patch("ecs_service_deployment_notifications.ecs.ServiceArn")
def test_handler_logs_at_debug_when_service_in_wrong_cluster(
    mock_service_arn: unittest.mock.MagicMock,
    mock_send_notification: unittest.mock.MagicMock,
    caplog: pytest.LogCaptureFixture,
):
    service_arn = "arn:test"
    cluster_name = "cluster-name"
    service_name = "service-name"
    slack_channel = "test-channel"
    lambda_arn = "arn:aws:lambda:eu-west-2:123456789012:function:example-function:1"

    event = {
        "resources": [
            f"{service_arn}-1",
            f"{service_arn}-2",
        ],
        "detail": {
            "eventName": "SERVICE_DEPLOYMENT_COMPLETED",
            "reason": "No reason",
        },
    }
    context = {}

    mock_service_arn.side_effect = [
        MockServiceArn(arn=f"{service_arn}-1", cluster_name=cluster_name, service_name=f"{service_name}-1"),
        MockServiceArn(arn=f"{service_arn}-2", cluster_name=cluster_name, service_name=f"{service_name}-2"),
    ]

    with unittest.mock.patch.dict(
        os.environ,
        {
            "CLUSTER_NAME": f"not-{cluster_name}",
            "SLACK_CHANNEL": slack_channel,
            "SLACK_NOTIFICATIONS_LAMBDA_ARN": lambda_arn,
            "LOG_LEVEL": "DEBUG",
        },
        clear=True,
    ):
        handler(event, context)

    assert (
        "root",
        logging.DEBUG,
        f"Ignoring SERVICE_DEPLOYMENT_COMPLETED event for {service_arn}-1",
    ) in caplog.record_tuples
    assert (
        "root",
        logging.DEBUG,
        f"Ignoring SERVICE_DEPLOYMENT_COMPLETED event for {service_arn}-2",
    ) in caplog.record_tuples
