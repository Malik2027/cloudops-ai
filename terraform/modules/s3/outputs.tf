output "assets_bucket_id" {
  value       = aws_s3_bucket.assets.id
  description = "Name/ID of the app assets S3 bucket"
}

output "assets_bucket_arn" {
  value       = aws_s3_bucket.assets.arn
  description = "ARN of the app assets S3 bucket"
}

output "logs_bucket_id" {
  value       = aws_s3_bucket.logs.id
  description = "Name/ID of the ALB access logs S3 bucket"
}

output "logs_bucket_arn" {
  value       = aws_s3_bucket.logs.arn
  description = "ARN of the ALB access logs S3 bucket"
}
