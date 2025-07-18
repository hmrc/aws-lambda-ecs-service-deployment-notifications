
# aws-lambda-ecs-service-deployment-notifications

This Lambda sends Slack notifications when receiving ECS service deployment events for a configured cluster.

## Configuration

### Environment variables

`CLUSTER_NAME` - name of the ECS cluster to produce notifications for
`SLACK_CHANNEL` - name of the Slack channel to post service deployment notifications in
