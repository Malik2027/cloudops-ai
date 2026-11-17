module "vpc" {
  source                   = "../../modules/vpc"
  vpc_cidr                 = "10.0.0.0/16"
  environment              = var.environment
  availability_zone_a      = "ap-south-1a"
  availability_zone_b      = "ap-south-1b"
  public_subnet_cidr       = "10.0.1.0/24"
  public_subnet_cidr_2     = "10.0.4.0/24"
  private_subnet_ec2_cidr  = "10.0.2.0/24"
  private_subnet_alb_cidr  = "10.0.3.0/24"
}

module "security_group" {
  source           = "../../modules/security-group"
  environment      = var.environment
  vpc_id           = module.vpc.vpc_id
  ssh_allowed_cidr = var.ssh_allowed_cidr
}

module "iam" {
  source      = "../../modules/iam"
  environment = var.environment
}

module "s3" {
  source             = "../../modules/s3"
  environment        = var.environment
  bucket_name_prefix = "cloudops-ai"
}

module "ec2" {
  count = 2

  source               = "../../modules/ec2"
  ami_id               = var.ami_id
  instance_type        = var.instance_type
  key_name             = var.key_name
  environment          = var.environment
  subnet_id            = module.vpc.private_subnet_ids[0]
  security_group_ids   = [module.security_group.ec2_sg_id]
  iam_instance_profile = module.iam.instance_profile_name
  root_volume_size     = var.root_volume_size
}

module "alb" {
  source            = "../../modules/alb"
  environment       = var.environment
  vpc_id            = module.vpc.vpc_id
  public_subnet_ids = [module.vpc.public_subnet_id, module.vpc.public_subnet_2_id]
  security_group_id = module.security_group.alb_sg_id
  logs_bucket_id    = module.s3.logs_bucket_id
  instance_ids      = [for i in range(2) : module.ec2[i].instance_id]
  certificate_arn   = var.certificate_arn
  health_check_path = var.health_check_path

  depends_on = [module.s3]
}

module "monitoring" {
  source         = "../../modules/monitoring"
  environment    = var.environment
  instance_ids   = [for i in range(2) : module.ec2[i].instance_id]
  alb_arn_suffix = module.alb.alb_arn_suffix
  alert_email    = var.alert_email
}
