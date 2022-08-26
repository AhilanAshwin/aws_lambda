module "sqs" {
  source  = "terraform-aws-modules/sqs/aws"
  version = "3.3.0"
  name    = "${local.prefix}-sqs"
  tags    = local.common_tags
}