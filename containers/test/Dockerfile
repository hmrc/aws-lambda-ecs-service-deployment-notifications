# hadolint ignore=DL3006
FROM aws-lambda-ecs-service-deployment-notifications-test-base

WORKDIR /app
COPY pyproject.toml .
COPY src .

# hadolint wants us to pin the version of the installed package??
# hadolint ignore=DL3013
RUN pip --verbose install --no-cache-dir --editable . \
 && pip --verbose install --no-cache-dir --group dev
