terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

provider "aws" {
  # Configuration options
  region  = var.aws_region
  profile = "default"
}

# These are a set of local values that can be declared together
locals {
  prefix      = "${var.app_prefix}-${var.environment}"
  environment = var.environment
  common_tags = {
    author      = var.author
    environment = var.environment
    app_name    = var.app_name
  }
}
