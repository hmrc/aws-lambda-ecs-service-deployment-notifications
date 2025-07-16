# hadolint ignore=DL3006
FROM aws-lambda-ecs-service-deployment-notifications-release-base

WORKDIR ${LAMBDA_TASK_ROOT}

COPY pyproject.toml .
COPY src src

RUN pip --verbose install --no-cache-dir .

CMD [ "ecs_service_deployment_notifications.handler.handler" ]
