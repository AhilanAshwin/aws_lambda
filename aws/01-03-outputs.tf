output "ecr_repository_url" {
  description = "The URL of the ecr reposiory"
  value       = aws_ecr_repository.ecr_repo.repository_url
}

output "api_gateway_stage_url" {
  description = "API Gateway stage invocation URL"
  value       = aws_api_gateway_stage.api_stage.invoke_url
}

output "sqs_queue_id" {
  description = "The URL of the sqs queue"
  value       = module.sqs.sqs_queue_id
}
