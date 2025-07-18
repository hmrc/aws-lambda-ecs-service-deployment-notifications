module "lambda" {
  source = "git::ssh://git@github.com/hmrc/terraform-aws-lambda-container.git"

  account_engineering_boundary = var.account_engineering_boundary

  environment                             = var.environment
  function_name                           = "${var.cluster_name}-deployment-notifications"
  image_command                           = ["ecs_service_deployment_notifications.handler.handler"]
  image_uri                               = "419929493928.dkr.ecr.eu-west-2.amazonaws.com/aws-lambda-ecs-service-deployment-notifications:${var.image_tag}"
  lambda_git_repo                         = "https://www.github.com/hmrc/aws-lambda-ecs-service-deployment-notifications"
  log_subscription_filter_destination_arn = var.log_subscription_filter_destination_arn

  environment_variables = {
    CLUSTER_NAME                   = var.cluster_name
    SLACK_CHANNEL                  = var.slack_channel
    SLACK_NOTIFICATIONS_LAMBDA_ARN = var.slack_notifications_lambda_arn
  }
}

data "aws_iam_policy_document" "invoke_slack_notifications_lambda" {
  statement {
    actions = [
      "lambda:InvokeFunction",
    ]
    effect = "Allow"
    resources = [
      var.slack_notifications_lambda_arn
    ]
    sid = "AllowInvokeSlackNotificationsLambda"
  }
}

resource "aws_iam_role_policy" "invoke_slack_notifications_lambda" {
  name   = "lambda-invoke-slack-notifications-lambda"
  policy = data.aws_iam_policy_document.invoke_slack_notifications_lambda.json
  role   = module.lambda.iam_role_id
}
