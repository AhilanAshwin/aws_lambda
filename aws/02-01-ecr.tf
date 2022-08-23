resource "aws_ecr_repository" "ecr_repo" {
  name                 = var.app_prefix
  image_tag_mutability = "MUTABLE"
  force_delete         = true
  tags                 = local.common_tags

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "null_resource" "ecr_image" {
  provisioner "local-exec" {
    command = <<EOF
           aws ecr get-login-password --region ${var.aws_region} | docker login --username AWS --password-stdin ${aws_ecr_repository.ecr_repo.registry_id}.dkr.ecr.${var.aws_region}.amazonaws.com
           docker tag ${var.app_prefix}:latest ${aws_ecr_repository.ecr_repo.repository_url}:latest
           docker push ${aws_ecr_repository.ecr_repo.repository_url}:latest
       EOF
  }
}

data "aws_ecr_image" "lambda_image" {
  depends_on = [
    null_resource.ecr_image
  ]
  repository_name = aws_ecr_repository.ecr_repo.name
  image_tag       = "latest"
}

output "ecr_registry_id" {
  description = "The registry ID of where the repository was created"
  value       = aws_ecr_repository.ecr_repo.registry_id
}

output "ecr_repository_url" {
  description = "The URL of the ecr reposiory"
  value       = aws_ecr_repository.ecr_repo.repository_url
}

