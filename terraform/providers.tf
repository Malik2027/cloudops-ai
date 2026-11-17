terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
  # Credentials via env vars: AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY
  # or AWS_PROFILE pointing to ~/.aws/credentials
}
