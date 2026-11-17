variable "vpc_cidr" {
  description = "VPC CIDR range"
  type        = string
}

variable "environment" {
  description = "Deployment environment"
  type        = string
}
variable "availability_zone_a" {
  description = "Availability Zone A"
  type        = string
}
variable "availability_zone_b" {
  description = "Availability Zone B"
  type        = string
}
variable "public_subnet_cidr" {
  description = "CIDR block for the public subnet"
  type        = string
}
variable "private_subnet_ec2_cidr" {
  description = "CIDR block for the private subnet for EC2"
  type        = string
}
variable "private_subnet_alb_cidr" {
  description = "CIDR block for the private subnet for ALB"
  type        = string
}

variable "public_subnet_cidr_2" {
  description = "CIDR block for the second public subnet (AZ-b) used by ALB for multi-AZ"
  type        = string
  default     = "10.0.4.0/24"
}