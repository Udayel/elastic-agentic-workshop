/**
 * Travel Intelligence Agent - Main Terraform Configuration
 * Deploys complete infrastructure on AWS
 */

terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "Travel-Intelligence-Agent"
      Environment = var.environment
      ManagedBy   = "Terraform"
      Workshop    = "Elastic-AgenticBuilder"
    }
  }
}

/**
 * Variables
 */
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "workshop"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "travel-agent"
}

variable "elastic_cloud_id" {
  description = "Elastic Cloud ID"
  type        = string
  sensitive   = true
}

variable "elastic_username" {
  description = "Elastic username"
  type        = string
  default     = "elastic"
  sensitive   = true
}

variable "elastic_password" {
  description = "Elastic password"
  type        = string
  sensitive   = true
}

variable "strands_api_key" {
  description = "Strands API key for flights/hotels"
  type        = string
  sensitive   = true
}

variable "twilio_account_sid" {
  description = "Twilio Account SID for SMS"
  type        = string
  sensitive   = true
}

variable "twilio_auth_token" {
  description = "Twilio Auth Token"
  type        = string
  sensitive   = true
}

variable "twilio_phone_number" {
  description = "Twilio phone number"
  type        = string
}

/**
 * Data Sources
 */
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

/**
 * Locals
 */
locals {
  account_id = data.aws_caller_identity.current.account_id
  region     = data.aws_region.current.name

  common_tags = {
    Project     = var.project_name
    Environment = var.environment
  }

  lambda_functions = {
    agent-core        = "Agent orchestrator with Bedrock Claude"
    destination-expert = "Destination search with ELSER"
    booking-assistant = "Flight and hotel search via Strands"
    activities-expert = "Activities search with ELSER"
    deal-comparator   = "Price comparison across providers"
    itinerary-builder = "Smart itinerary generation"
    notification      = "SMS/Email notifications"
    preference-mgr    = "User preference management"
  }
}

/**
 * VPC and Networking
 */
module "vpc" {
  source = "./modules/vpc"

  project_name = var.project_name
  environment  = var.environment
  cidr_block   = "10.0.0.0/16"

  availability_zones = [
    "${var.aws_region}a",
    "${var.aws_region}b"
  ]
}

/**
 * Secrets Manager
 */
resource "aws_secretsmanager_secret" "elastic_credentials" {
  name        = "${var.project_name}-elastic-credentials"
  description = "Elastic Cloud credentials"

  recovery_window_in_days = 0 # For workshop - immediate deletion
}

resource "aws_secretsmanager_secret_version" "elastic_credentials" {
  secret_id = aws_secretsmanager_secret.elastic_credentials.id

  secret_string = jsonencode({
    cloud_id = var.elastic_cloud_id
    username = var.elastic_username
    password = var.elastic_password
    endpoint = "https://${split(":", var.elastic_cloud_id)[1]}"
  })
}

resource "aws_secretsmanager_secret" "strands_api" {
  name        = "${var.project_name}-strands-api"
  description = "Strands API credentials"

  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "strands_api" {
  secret_id = aws_secretsmanager_secret.strands_api.id

  secret_string = jsonencode({
    api_key = var.strands_api_key
  })
}

resource "aws_secretsmanager_secret" "twilio_credentials" {
  name        = "${var.project_name}-twilio"
  description = "Twilio SMS credentials"

  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "twilio_credentials" {
  secret_id = aws_secretsmanager_secret.twilio_credentials.id

  secret_string = jsonencode({
    account_sid  = var.twilio_account_sid
    auth_token   = var.twilio_auth_token
    phone_number = var.twilio_phone_number
  })
}

/**
 * DynamoDB Tables
 */
resource "aws_dynamodb_table" "agent_state" {
  name           = "${var.project_name}-agent-state"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "session_id"
  range_key      = "timestamp"

  attribute {
    name = "session_id"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "N"
  }

  attribute {
    name = "user_id"
    type = "S"
  }

  global_secondary_index {
    name            = "user-index"
    hash_key        = "user_id"
    range_key       = "timestamp"
    projection_type = "ALL"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  tags = local.common_tags
}

resource "aws_dynamodb_table" "trip_data" {
  name           = "${var.project_name}-trip-data"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "trip_id"

  attribute {
    name = "trip_id"
    type = "S"
  }

  attribute {
    name = "user_id"
    type = "S"
  }

  global_secondary_index {
    name            = "user-trips"
    hash_key        = "user_id"
    projection_type = "ALL"
  }

  tags = local.common_tags
}

/**
 * S3 Bucket for artifacts
 */
resource "aws_s3_bucket" "artifacts" {
  bucket = "${var.project_name}-artifacts-${local.account_id}"

  tags = local.common_tags
}

resource "aws_s3_bucket_versioning" "artifacts" {
  bucket = aws_s3_bucket.artifacts.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "artifacts" {
  bucket = aws_s3_bucket.artifacts.id

  rule {
    id     = "delete-old-versions"
    status = "Enabled"

    noncurrent_version_expiration {
      noncurrent_days = 30
    }
  }
}

/**
 * IAM Role for Lambda Functions
 */
resource "aws_iam_role" "lambda_role" {
  name = "${var.project_name}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = local.common_tags
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  role       = aws_iam_role.lambda_role.name
}

resource "aws_iam_role_policy_attachment" "lambda_vpc" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
  role       = aws_iam_role.lambda_role.name
}

resource "aws_iam_role_policy" "lambda_custom" {
  name = "${var.project_name}-lambda-custom-policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = [
          aws_secretsmanager_secret.elastic_credentials.arn,
          aws_secretsmanager_secret.strands_api.arn,
          aws_secretsmanager_secret.twilio_credentials.arn
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Resource = [
          aws_dynamodb_table.agent_state.arn,
          aws_dynamodb_table.trip_data.arn,
          "${aws_dynamodb_table.agent_state.arn}/index/*",
          "${aws_dynamodb_table.trip_data.arn}/index/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream"
        ]
        Resource = "arn:aws:bedrock:${local.region}::foundation-model/*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject"
        ]
        Resource = "${aws_s3_bucket.artifacts.arn}/*"
      }
    ]
  })
}

/**
 * CloudWatch Log Groups
 */
resource "aws_cloudwatch_log_group" "lambda_logs" {
  for_each = local.lambda_functions

  name              = "/aws/lambda/${var.project_name}-${each.key}"
  retention_in_days = 7

  tags = local.common_tags
}

/**
 * Lambda Layers
 */
resource "aws_lambda_layer_version" "dependencies" {
  filename            = "${path.module}/../build/lambda-layer.zip"
  layer_name          = "${var.project_name}-dependencies"
  compatible_runtimes = ["python3.11"]
  description         = "Python dependencies for travel agent"

  source_code_hash = filebase64sha256("${path.module}/../build/lambda-layer.zip")
}

/**
 * API Gateway
 */
resource "aws_apigatewayv2_api" "travel_agent" {
  name          = "${var.project_name}-api"
  protocol_type = "HTTP"
  description   = "Travel Intelligence Agent API"

  cors_configuration {
    allow_origins = ["*"]
    allow_methods = ["GET", "POST", "OPTIONS"]
    allow_headers = ["*"]
    max_age       = 3600
  }

  tags = local.common_tags
}

resource "aws_apigatewayv2_stage" "prod" {
  api_id      = aws_apigatewayv2_api.travel_agent.id
  name        = "prod"
  auto_deploy = true

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_logs.arn
    format = jsonencode({
      requestId      = "$context.requestId"
      ip             = "$context.identity.sourceIp"
      requestTime    = "$context.requestTime"
      httpMethod     = "$context.httpMethod"
      routeKey       = "$context.routeKey"
      status         = "$context.status"
      protocol       = "$context.protocol"
      responseLength = "$context.responseLength"
    })
  }

  tags = local.common_tags
}

resource "aws_cloudwatch_log_group" "api_logs" {
  name              = "/aws/apigateway/${var.project_name}"
  retention_in_days = 7

  tags = local.common_tags
}

/**
 * Outputs
 */
output "api_endpoint" {
  description = "API Gateway endpoint URL"
  value       = aws_apigatewayv2_stage.prod.invoke_url
}

output "dynamodb_tables" {
  description = "DynamoDB table names"
  value = {
    agent_state = aws_dynamodb_table.agent_state.name
    trip_data   = aws_dynamodb_table.trip_data.name
  }
}

output "s3_bucket" {
  description = "S3 bucket for artifacts"
  value       = aws_s3_bucket.artifacts.bucket
}

output "secrets" {
  description = "Secrets Manager ARNs"
  value = {
    elastic = aws_secretsmanager_secret.elastic_credentials.arn
    strands = aws_secretsmanager_secret.strands_api.arn
    twilio  = aws_secretsmanager_secret.twilio_credentials.arn
  }
  sensitive = true
}
