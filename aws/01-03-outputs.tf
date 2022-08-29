output "ecr_repository_url" {
  description = "The URL of the ecr reposiory"
  value       = aws_ecr_repository.ecr_repo.repository_url
}

output "ecr_repository_arm" {
  description = "The ARN of the ecr reposiory"
  value       = aws_ecr_repository.ecr_repo.arn
}

output "api_gateway_arn" {
  description = "The ARN of the api gateway"
  value       = aws_api_gateway_rest_api.api_gateway.arn
}

output "api_gateway_stage_url" {
  description = "API Gateway stage invocation URL"
  value       = aws_api_gateway_stage.api_dev.invoke_url
}

output "sqs_queue_id" {
  description = "The URL of the sqs queue"
  value       = module.sqs.sqs_queue_id
}

output "sqs_queue_arn" {
  description = "The URL of the sqs queue"
  value       = module.sqs.sqs_queue_arn
}

output "sqs_queue_id_local" {
  description = "The URL of the sqs queue for local testing"
  value       = module.sqs_local.sqs_queue_id
}

output "sqs_queue_arn_local" {
  description = "The URL of the sqs queue for local testing"
  value       = module.sqs_local.sqs_queue_arn
}
