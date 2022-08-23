# Add efs, vpc for production
resource "aws_iam_role" "lambda" {
  name               = "${local.prefix}-lambda-role"
  assume_role_policy = <<EOF
{
   "Version": "2012-10-17",
   "Statement": [
       {
           "Action": "sts:AssumeRole",
           "Principal": {
               "Service": "lambda.amazonaws.com"
           },
           "Effect": "Allow"
       }
   ]
}
 EOF
}

# resource "aws_iam_role" "api_lambda_role" {
#   name               = "ApiLambdaRole"
#   assume_role_policy = data.aws_iam_policy_document.lambda_assume_policy.json
# }

# resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
#   role       = aws_iam_role.api_lambda_role.name
#   policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
# }

# resource "aws_iam_role_policy_attachment" "lambda_sqs_producer_policy_attachment" {
#   role       = aws_iam_role.api_lambda_role.name
#   policy_arn = aws_iam_policy.lambda_sqs_producer_policy.arn
# }

resource "aws_lambda_function" "api_lambda" {
  function_name = local.prefix
  role          = aws_iam_role.lambda.arn
  image_uri     = "${aws_ecr_repository.ecr_repo.repository_url}@${data.aws_ecr_image.lambda_image.id}"
  package_type  = "Image"
}
