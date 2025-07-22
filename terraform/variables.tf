variable "account_engineering_boundary" {
  description = "The account engineering permission boundary to use for the IAM role"
  type        = string
}

variable "environment" {
  description = "Name of the environment the lambda function is deployed to"
  type        = string
}

variable "image_tag" {
  description = "The image tag to deploy"
  type        = string
}

variable "log_subscription_filter_destination_arn" {
  description = "The Kibana log subscription destination ARN"
  type        = string
}

variable "cluster_name" {
  description = "Name of the ECS cluster to produce notifications for"
  type        = string
}

variable "slack_channel" {
  description = "Name of the Slack channel to post service deployment notifications in"
  type        = string
}

variable "slack_notifications_lambda_arn" {
  description = "ARN of the Slack notifications Lambda"
  type        = string
}

variable "service_name_prefix" {
  description = <<EOT
  Services to notify about must start with this prefix.

  Any service that starts with this prefix will be monitored for deployment events. If it does not start with this prefix, it will not be monitored.
  Leave this empty to monitor all services in the cluster.
  EOT

  type    = string
  default = ""
}
