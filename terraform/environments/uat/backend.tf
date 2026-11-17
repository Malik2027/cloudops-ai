terraform {
  backend "s3" {
    bucket       = "devcloudops-ai-terraform-state"
    key          = "uat/terraform.tfstate"
    region       = "us-east-1"
    use_lockfile = true
    encrypt      = true
  }
}
