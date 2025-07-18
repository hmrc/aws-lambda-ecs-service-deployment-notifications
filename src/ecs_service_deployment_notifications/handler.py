import dataclasses
import json
import logging
import os

from . import ecs, slack

logging.basicConfig()


@dataclasses.dataclass
class EventType:
    description: str
    color: str | None


event_types = {
    "SERVICE_DEPLOYMENT_IN_PROGRESS": EventType(
        description="ECS service deployment in progress",
        color=None,
    ),
    "SERVICE_DEPLOYMENT_COMPLETED": EventType(
        description="ECS service deployment completed",
        color="good",
    ),
    "SERVICE_DEPLOYMENT_FAILED": EventType(
        description="ECS service deployment failed",
        color="danger",
    ),
}


def handler(event: dict, context: dict) -> None:
    logger = logging.getLogger()
    logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))

    logging.debug(json.dumps(event))

    if "detail" not in event or "eventName" not in event["detail"]:
        raise ValueError("Missing event name")

    event_name = event["detail"]["eventName"]
    if event_name not in event_types:
        raise ValueError(f"Unexpected event name {event_name}")

    event_type = event_types[event_name]

    service_arns = [ecs.ServiceArn(service_arn) for service_arn in event["resources"]]

    for service_arn in service_arns:
        if service_arn.cluster_name == os.environ["CLUSTER_NAME"]:
            logging.info(f"Sending {event_name} notification for {service_arn.arn}")
            slack.send_notification(
                lambda_arn=os.environ["SLACK_NOTIFICATIONS_LAMBDA_ARN"],
                description=event_type.description,
                color=event_type.color,
                channel=os.environ["SLACK_CHANNEL"],
                cluster_name=service_arn.cluster_name,
                service_name=service_arn.service_name,
                reason=event["detail"]["reason"],
            )
        else:
            logging.debug(f"Ignoring {event_name} event for {service_arn.arn}")
