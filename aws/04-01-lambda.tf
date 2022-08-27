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

resource "aws_iam_role" "lambda_role" {
  name               = "LambdaRole"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_policy.json
}

resource "aws_iam_role_policy_attachment" "lambda_sqs_role_policy" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSQSFullAccess"
}

resource "aws_iam_role_policy_attachment" "lambda_logs_policy" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"
}

resource "aws_cloudwatch_log_group" "api_log_group" {
  name              = "/aws/lambda/${aws_lambda_function.api_lambda.function_name}"
  retention_in_days = 7
  lifecycle {
    prevent_destroy = false
  }
}

resource "aws_cloudwatch_log_group" "worker_log_group" {
  name              = "/aws/lambda/${aws_lambda_function.worker_lambda.function_name}"
  retention_in_days = 7
  lifecycle {
    prevent_destroy = false
  }
}

resource "aws_lambda_function_event_invoke_config" "lambda" {
  function_name = aws_lambda_function.api_lambda.function_name
  destination_config {
    on_success {
      destination = module.sqs.sqs_queue_arn
    }
    on_failure {
      destination = module.sqs.sqs_queue_arn
    }
  }
}

resource "aws_lambda_event_source_mapping" "event_source_mapping" {
  event_source_arn = module.sqs.sqs_queue_arn
  function_name    = aws_lambda_function.worker_lambda.arn
}

resource "aws_lambda_permission" "api_lambda_permission" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.api_gateway.execution_arn}/*/*"
}

resource "aws_lambda_function" "api_lambda" {
  function_name = "${local.prefix}-api"
  role          = aws_iam_role.lambda_role.arn
  image_uri     = "${aws_ecr_repository.ecr_repo.repository_url}@${data.aws_ecr_image.lambda_image.id}"
  package_type  = "Image"
}

resource "aws_lambda_function" "worker_lambda" {
  function_name = "${local.prefix}-worker"
  role          = aws_iam_role.lambda_role.arn
  image_uri     = "${aws_ecr_repository.ecr_repo.repository_url}@${data.aws_ecr_image.lambda_image.id}"
  package_type  = "Image"

  image_config {
    command = ["app.lambda_function.consumer_handler"]
  }
}
