variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "ap-south-1"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "dev"
}

variable "ami_id" {
  description = "AMI ID for EC2 instances (Ubuntu 22.04 LTS in ap-south-1)"
  type        = string
  default     = "ami-0f58b397bc5c1f2e8"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

variable "key_name" {
  description = "EC2 key pair name"
  type        = string
  default     = "HRMS"
}

variable "root_volume_size" {
  description = "Root EBS volume size in GB"
  type        = number
  default     = 20
}

variable "ssh_allowed_cidr" {
  description = "CIDR allowed to SSH to EC2 instances (your office/VPN IP)"
  type        = string
  default     = "10.0.0.0/8"
}

variable "certificate_arn" {
  description = "ACM certificate ARN for HTTPS. Leave empty for HTTP-only (dev default)."
  type        = string
  default     = ""
}

variable "health_check_path" {
  description = "HTTP path for the ALB health check"
  type        = string
  default     = "/health"
}

variable "alert_email" {
  description = "Email to receive CloudWatch alarm notifications"
  type        = string
  default     = ""
}
