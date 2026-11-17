variable "environment" {
  description = "Deployment environment"
  type        = string
}

variable "instance_ids" {
  description = "List of EC2 instance IDs to monitor"
  type        = list(string)
}

variable "alb_arn_suffix" {
  description = "ARN suffix of the ALB (from aws_lb.this.arn_suffix) for CloudWatch metrics"
  type        = string
}

variable "alert_email" {
  description = "Email address to receive CloudWatch alarm notifications. Leave empty to skip."
  type        = string
  default     = ""
}
