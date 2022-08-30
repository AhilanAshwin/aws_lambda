module "sqs" {
  for_each = toset(local.environments)
  source   = "terraform-aws-modules/sqs/aws"
  version  = "3.3.0"
  name     = "${local.prefix}-sqs-${each.key}"
  tags     = local.common_tags
}

module "sqs_local" {
  source  = "terraform-aws-modules/sqs/aws"
  version = "3.3.0"
  name    = "${local.prefix}-sqs-local"
  tags    = local.common_tags
}
