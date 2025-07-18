resource "aws_cloudwatch_event_rule" "ecs_service_deployment" {
  name        = "ecs-service-deployment-notifications-${var.cluster_name}"
  description = "Matches ECS service deployment events"
  event_pattern = jsonencode({
    source        = ["aws.ecs"],
    "detail-type" = ["ECS Deployment State Change"],
    resources = [{
      prefix = "arn:aws:ecs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:service/${var.cluster_name}/"
    }]
  })
}

resource "aws_cloudwatch_event_target" "ecs_service_deployment_notifications" {
  target_id = "ecs-service-deployment-notifications-${var.cluster_name}"
  rule      = aws_cloudwatch_event_rule.ecs_service_deployment.name
  arn       = module.lambda.lambda_alias_arn
}

resource "aws_lambda_permission" "allow_lambda_to_execute_from_eventbridge_on_event" {
  statement_id  = "AllowExecutionFromServiceDeploymentEvents"
  action        = "lambda:InvokeFunction"
  function_name = module.lambda.lambda_alias_arn
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.ecs_service_deployment.arn
}
