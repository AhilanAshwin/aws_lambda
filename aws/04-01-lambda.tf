data "aws_iam_policy_document" "lambda_assume_policy" {
  statement {
    effect = "Allow"
    actions = [
      "sts:AssumeRole",
    ]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

# data "aws_iam_policy_document" "lambda_sqs_producer_policy" {
#   statement {
#     effect = "Allow"
#     actions = [
#       "sqs:GetQueueAttributes",
#       "sqs:GetQueueUrl",
#       "sqs:SendMessage*"
#     ]
#     resources = [
#       module.sqs.sqs_queue_arn
#     ]
#   }
# }

resource "aws_iam_role" "lambda_role" {
  name               = "ApiLambdaRole"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_policy.json
}

# resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
#   role       = aws_iam_role.api_lambda_role.name
#   policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
# }

# resource "aws_iam_role_policy_attachment" "lambda_sqs_producer_policy_attachment" {
#   role       = aws_iam_role.api_lambda_role.name
#   policy_arn = aws_iam_policy.lambda_sqs_producer_policy.arn
# }

# resource "aws_lambda_event_source_mapping" "executor_lambda" {
#   event_source_arn = module.sqs.sqs_queue_arn
#   function_name = aws_lambda_function.api_lambda
# }

resource "aws_lambda_function" "api_lambda" {
  function_name = "${local.prefix}-api"
  role          = aws_iam_role.lambda_role.arn
  image_uri     = "${aws_ecr_repository.ecr_repo.repository_url}@${data.aws_ecr_image.lambda_image.id}"
  package_type  = "Image"
}

# resource "aws_lambda_function" "worker_lambda" {
#   function_name = "${local.prefix}-worker"
#   role          = aws_iam_role.lambda_role.arn
#   image_uri     = "${aws_ecr_repository.ecr_repo.repository_url}@${data.aws_ecr_image.lambda_image.id}"
#   package_type  = "Image"

#   image_config {
#     command = ["app.lambda_function.consumer_handler"]
#   }
# }

# resource "aws_lambda_event_source_mapping" "event_source_mapping" {
#   event_source_arn = module.sqs.sqs_queue_arn
#   enabled          = true
#   function_name    = aws_lambda_function.worker_lambda.function_name
#   batch_size       = 1
# }

resource "aws_lambda_permission" "api_lambda_permission" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.api_gateway.execution_arn}/*/*"
}
