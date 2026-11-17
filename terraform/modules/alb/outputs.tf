output "alb_dns_name" {
  value       = aws_lb.this.dns_name
  description = "DNS name of the Application Load Balancer"
}

output "alb_arn" {
  value       = aws_lb.this.arn
  description = "ARN of the Application Load Balancer"
}

output "alb_arn_suffix" {
  value       = aws_lb.this.arn_suffix
  description = "ARN suffix for use in CloudWatch metrics"
}

output "target_group_arn" {
  value       = aws_lb_target_group.this.arn
  description = "ARN of the ALB target group"
}
