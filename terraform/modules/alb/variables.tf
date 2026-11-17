variable "environment" {
  description = "Deployment environment"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID to create the target group in"
  type        = string
}

variable "public_subnet_ids" {
  description = "List of public subnet IDs for the ALB (at least 2, different AZs)"
  type        = list(string)
}

variable "security_group_id" {
  description = "Security group ID for the ALB"
  type        = string
}

variable "logs_bucket_id" {
  description = "S3 bucket name for ALB access logs"
  type        = string
}

variable "instance_ids" {
  description = "List of EC2 instance IDs to register as targets"
  type        = list(string)
}

variable "certificate_arn" {
  description = "ACM certificate ARN for HTTPS. Leave empty to use HTTP only."
  type        = string
  default     = ""
}

variable "health_check_path" {
  description = "HTTP path for the target group health check"
  type        = string
  default     = "/health"
}
