## variables can be set on the CLI or in terraform.tfvars
variable "profile" {
  description = "AWS profile"
  default     = "default"
}

variable "region" {
  description = "AWS region"
  default     = "us-west-2"
}

variable "availability_zone_b" {
  description = "secondary AWS availability zone"
  default     = "us-west-2a"
}

variable "availability_zone_a" {
  description = "primary AWS availability zone"
  default     = "us-west-2b"
}

variable "port" {
  description = "REST API port"
  default     = 5000
}

provider "aws" {
  region  = var.region
  profile = var.profile
}

variable "aws_secret_access_key" {
  description = "AWS secret access key to pass to ECR task"
  sensitive   = true
}

variable "aws_access_key_id" {
  description = "AWS secret access id to pass to ECR task"
  sensitive   = true
}

# may need to create the bucket first
# aws s3api create-bucket --bucket "email-server-terraform" --region "us-west-2" --create-bucket-configuration LocationConstraint="us-west-2"
terraform {
  required_version = ">= 1.0"

  backend "s3" {
    bucket  = "email-server-terraform"
    key     = "terraform.tfstate"
    region  = "us-west-2"
    profile = "default"
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.69.0"
    }
  }
}
