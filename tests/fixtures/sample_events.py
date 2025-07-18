# 123456789012 is the default account number used by moto
account = "123456789012"
region = "eu-west-2"
cluster_name_notified = "notified"
cluster_name_unnotified = "unnotified"
service_name = "service-name"

_event_base = {
    "version": "0",
    "id": "ddca6449-b258-46c0-8653-e0e3a6EXAMPLE",
    "detail-type": "ECS Deployment State Change",
    "source": "aws.ecs",
    "account": account,
    "time": "2020-05-23T12:31:14Z",
    "region": region,
}

event_in_progress = _event_base | {
    "detail": {
        "eventType": "INFO",
        "eventName": "SERVICE_DEPLOYMENT_IN_PROGRESS",
        "deploymentId": "ecs-svc/123",
        "updatedAt": "2020-05-23T11:11:11Z",
        "reason": "ECS deployment deploymentId in progress.",
    },
}

slack_payload_in_progress = {
    "channels": ["event-integ-recycle"],
    "username": "ecs_service_deployment_notifications",
    "text": "ECS service deployment in progress",
    "message_content": {
        "fields": [
            {"short": True, "title": "Service Name", "value": service_name},
            {"short": True, "title": "Cluster Name", "value": cluster_name_notified},
            {
                "short": False,
                "title": "Reason",
                "value": "ECS deployment deploymentId in progress.",
            },
        ]
    },
}

event_completed = _event_base | {
    "detail": {
        "eventType": "INFO",
        "eventName": "SERVICE_DEPLOYMENT_COMPLETED",
        "deploymentId": "ecs-svc/123",
        "updatedAt": "2020-05-23T11:11:11Z",
        "reason": "ECS deployment deploymentId completed.",
    },
}

slack_payload_completed = {
    "channels": ["event-integ-recycle"],
    "username": "ecs_service_deployment_notifications",
    "text": "ECS service deployment completed",
    "message_content": {
        "color": "good",
        "fields": [
            {"short": True, "title": "Service Name", "value": service_name},
            {"short": True, "title": "Cluster Name", "value": cluster_name_notified},
            {
                "short": False,
                "title": "Reason",
                "value": "ECS deployment deploymentId completed.",
            },
        ],
    },
}

event_failed = _event_base | {
    "detail": {
        "eventType": "ERROR",
        "eventName": "SERVICE_DEPLOYMENT_FAILED",
        "deploymentId": "ecs-svc/123",
        "updatedAt": "2020-05-23T11:11:11Z",
        "reason": "ECS deployment circuit breaker: task failed to start.",
    },
}

slack_payload_failed = {
    "channels": ["event-integ-recycle"],
    "username": "ecs_service_deployment_notifications",
    "text": "ECS service deployment failed",
    "message_content": {
        "color": "danger",
        "fields": [
            {"short": True, "title": "Service Name", "value": service_name},
            {"short": True, "title": "Cluster Name", "value": cluster_name_notified},
            {
                "short": False,
                "title": "Reason",
                "value": "ECS deployment circuit breaker: task failed to start.",
            },
        ],
    },
}


event_resources_notified = {
    "resources": [f"arn:aws:ecs:{region}:{account}:service/{cluster_name_notified}/{service_name}"],
}
event_resources_unnotified = {
    "resources": [f"arn:aws:ecs:{region}:{account}:service/{cluster_name_unnotified}/{service_name}"],
}
