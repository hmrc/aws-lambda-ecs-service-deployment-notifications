output "lambda_alias_name" {
  value = module.lambda.lambda_alias_name
}

output "lambda_arn" {
  value = module.lambda.lambda_alias_arn
}

output "lambda_name" {
  value = module.lambda.lambda_name
}

output "lambda_role_arn" {
  value = module.lambda.iam_role_arn
}

output "lambda_role" {
  value = module.lambda.iam_role_id
}
