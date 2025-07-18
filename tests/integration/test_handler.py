import json
import os
import unittest.mock

import fixtures.sample_events as sample_events
import pytest
from ecs_service_deployment_notifications.handler import handler


@pytest.fixture
def mock_lambda_client():
    with unittest.mock.patch("boto3.client") as mock_client:
        mock_lambda_client = unittest.mock.MagicMock()

        def mock_client_side_effect(client_service: str):
            assert client_service == "lambda"
            return mock_lambda_client

        mock_client.side_effect = mock_client_side_effect
        yield mock_lambda_client


@pytest.mark.parametrize(
    "event, expected_payload",
    [
        pytest.param(
            sample_events.event_in_progress | sample_events.event_resources_notified,
            sample_events.slack_payload_in_progress,
            id="in_progress_notified",
        ),
        pytest.param(
            sample_events.event_completed | sample_events.event_resources_notified,
            sample_events.slack_payload_completed,
            id="completed_notified",
        ),
        pytest.param(
            sample_events.event_failed | sample_events.event_resources_notified,
            sample_events.slack_payload_failed,
            id="failed_notified",
        ),
    ],
)
@unittest.mock.patch.dict(
    os.environ,
    {
        "CLUSTER_NAME": "notified",
        "SLACK_CHANNEL": "event-integ-recycle",
        "SLACK_NOTIFICATIONS_LAMBDA_ARN": "test-arn",
    },
    clear=True,
)
def test_handler_invokes_slack_notifications_lambda(
    mock_lambda_client: unittest.mock.MagicMock,
    event: dict,
    expected_payload: dict,
):
    mock_lambda_client.invoke.return_value = {"StatusCode": 200}

    context = {}
    handler(event, context)

    mock_lambda_client.invoke.assert_called_once()
    kwargs = mock_lambda_client.invoke.call_args.kwargs
    assert kwargs["FunctionName"] == "test-arn"
    assert kwargs["InvocationType"] == "Event"
    assert json.loads(kwargs["Payload"]) == expected_payload


@pytest.mark.parametrize(
    "sample_event",
    [
        pytest.param(
            sample_events.event_in_progress | sample_events.event_resources_unnotified,
            id="in_progress_unnotified",
        ),
        pytest.param(
            sample_events.event_completed | sample_events.event_resources_unnotified,
            id="completed_unnotified",
        ),
        pytest.param(
            sample_events.event_failed | sample_events.event_resources_unnotified,
            id="failed_unnotified",
        ),
    ],
)
@unittest.mock.patch.dict(
    os.environ,
    {
        "CLUSTER_NAME": "notified",
        "SLACK_CHANNEL": "event-integ-recycle",
        "SLACK_NOTIFICATIONS_LAMBDA_ARN": "test-arn",
    },
    clear=True,
)
def test_handler_does_not_invoke_slack_notifications_lambda(
    mock_lambda_client: unittest.mock.MagicMock,
    sample_event: dict,
):
    mock_lambda_client.invoke.return_value = {"StatusCode": 200}

    context = {}
    handler(sample_event, context)

    mock_lambda_client.invoke.assert_not_called()
