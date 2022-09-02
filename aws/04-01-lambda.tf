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

resource "aws_iam_role_policy_attachment" "lambda_vpc_policy" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

resource "aws_lambda_function_event_invoke_config" "lambda" {
  for_each      = toset(local.environments)
  function_name = aws_lambda_function.api_lambda[each.key].function_name
  destination_config {
    on_success {
      destination = module.sqs[each.key].sqs_queue_arn
    }
    on_failure {
      destination = module.sqs[each.key].sqs_queue_arn
    }
  }
}

resource "aws_lambda_event_source_mapping" "event_source_mapping" {
  for_each         = toset(local.environments)
  event_source_arn = module.sqs[each.key].sqs_queue_arn
  function_name    = aws_lambda_function.worker_lambda[each.key].arn
}

resource "aws_lambda_permission" "api_lambda_permission" {
  for_each      = toset(local.environments)
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api_lambda[each.key].function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.api_gateway.execution_arn}/*/*"
}

resource "aws_lambda_function" "api_lambda" {
  for_each      = toset(local.environments)
  function_name = "${local.prefix}-api-${each.key}"
  role          = aws_iam_role.lambda_role.arn
  image_uri     = "${aws_ecr_repository.ecr_repo.repository_url}@${data.aws_ecr_image.lambda_image.id}"
  package_type  = "Image"
  environment {
    variables = {
      "STAGE"   = "${each.key}",
      "SQS_URL" = "${local.prefix}-sqs-${each.key}"

    }
  }
}

resource "aws_lambda_function" "worker_lambda" {
  for_each      = toset(local.environments)
  function_name = "${local.prefix}-worker-${each.key}"
  role          = aws_iam_role.lambda_role.arn
  image_uri     = "${aws_ecr_repository.ecr_repo.repository_url}@${data.aws_ecr_image.lambda_image.id}"
  package_type  = "Image"

  vpc_config {
    # Every subnet should be able to reach an EFS mount target in the same Availability Zone. Cross-AZ mounts are not permitted.
    subnet_ids         = data.aws_subnets.subnets.ids
    security_group_ids = [module.security-group.security_group_id]
  }

  image_config {
    command = ["app.lambda_function.consumer_handler"]
  }
}

data "aws_subnets" "subnets" {
  filter {
    name   = "vpc-id"
    values = [module.vpc.vpc_id]
  }
  tags = {
    Type = "Private Subnets"
  }
}

module "security-group" {
  source      = "terraform-aws-modules/security-group/aws"
  version     = "4.13.0"
  name        = "${local.prefix}-sg"
  description = "Security group AWS Lambda to connect to the internet. HTTP open for entire Internet (IPv4 CIDR), egress ports are all world open"
  vpc_id      = module.vpc.vpc_id
  # #   Ingress Rules & CIDR blocks
  # ingress_rules       = ["ssh-tcp", "http-80-tcp"]
  # ingress_cidr_blocks = ["0.0.0.0/0"]
  # Egress Rules & CIDR blocks
  egress_rules = ["all-all"]
  tags         = local.common_tags
}
