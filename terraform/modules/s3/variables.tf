variable "environment" {
  description = "Deployment environment"
  type        = string
}

variable "bucket_name_prefix" {
  description = "Prefix for all S3 bucket names (e.g. your project name)"
  type        = string
  default     = "cloudops-ai"
}
