module "efs-security-group" {
  source              = "terraform-aws-modules/security-group/aws"
  version             = "4.9.0"
  name                = "${local.prefix}-efs-sg"
  vpc_id              = module.vpc.vpc_id
  ingress_rules       = ["nfs-tcp"]
  ingress_cidr_blocks = [module.vpc.vpc_cidr_block]
  egress_rules        = ["all-all"]
  tags                = local.common_tags
}

resource "aws_efs_file_system" "efs_for_lambda" {
  lifecycle_policy {
    transition_to_ia = "AFTER_7_DAYS"
  }
  encrypted = true
  tags = {
    Name = "efs_for_lambda"
  }
}

resource "aws_efs_mount_target" "alpha" {
  for_each        = toset(module.vpc.private_subnets)
  file_system_id  = aws_efs_file_system.efs_for_lambda.id
  subnet_id       = each.key
  security_groups = [module.efs-security-group.security_group_id]
}

resource "aws_efs_access_point" "access_point_for_lambda" {
  file_system_id = aws_efs_file_system.efs_for_lambda.id

  root_directory {
    path = "/lambda-files"
    creation_info {
      owner_gid   = 1000
      owner_uid   = 1000
      permissions = "777"
    }
  }

  posix_user {
    gid = 1000
    uid = 1000
  }
  tags = {
    Name = "lambda-AccessPoint"
  }
}
