# AWS credentials to pass to task
resource "aws_secretsmanager_secret" "aws_access_key_id" {
  name = "aws_access_key_id"
}

resource "aws_secretsmanager_secret_version" "aws_access_key_id" {
  secret_id     = aws_secretsmanager_secret.aws_access_key_id.id
  secret_string = var.aws_access_key_id
}

data "aws_secretsmanager_secret" "aws_access_key_id" {
  name       = "aws_access_key_id"
  depends_on = [aws_secretsmanager_secret.aws_access_key_id]
}

data "aws_secretsmanager_secret_version" "aws_access_key_id" {
  secret_id = data.aws_secretsmanager_secret.aws_access_key_id.id
}

resource "aws_secretsmanager_secret" "aws_secret_access_key" {
  name = "aws_secret_access_key"
}

resource "aws_secretsmanager_secret_version" "aws_secret_access_key" {
  secret_id     = aws_secretsmanager_secret.aws_secret_access_key.id
  secret_string = var.aws_secret_access_key
}

data "aws_secretsmanager_secret" "aws_secret_access_key" {
  name       = "aws_secret_access_key"
  depends_on = [aws_secretsmanager_secret.aws_secret_access_key]
}

data "aws_secretsmanager_secret_version" "aws_secret_access_key" {
  secret_id = data.aws_secretsmanager_secret.aws_secret_access_key.id
}

# a place to put our logs
resource "aws_cloudwatch_log_group" "email_server" {
  name = "/ecs/email-server"
}

locals {
  environment = [
    {
      name  = "PYTHONPATH"
      value = "/code/email"
    },
    {
      name  = "QUEUE_NAME_PREFIX"
      value = "prod"
    },
    {
      name  = "EMAIL"
      value = var.email
    }
  ]
  logConfiguration = {
    logDriver = "awslogs"
    options = {
      awslogs-region        = var.region
      awslogs-group         = "/ecs/email-server"
      awslogs-stream-prefix = "ecs"
    }
  }
  image      = "enginetwork/email-server:latest"
  entryPoint = ["sh", "-c"]
  secrets = [{
    name      = "AWS_ACCESS_KEY_ID"
    valueFrom = data.aws_secretsmanager_secret_version.aws_access_key_id.arn
    }, {
    name      = "AWS_SECRET_ACCESS_KEY"
    valueFrom = data.aws_secretsmanager_secret_version.aws_secret_access_key.arn
  }]
}

# task definition
resource "aws_ecs_task_definition" "email_server" {
  family = "email-server"

  container_definitions = jsonencode([{
    name = "worker"
    portMappings = [
      {
        containerPort = var.port
        hostPort      = var.port
        protocol      = "tcp"
      }
    ]
    essential        = true
    image            = local.image
    cpu              = 10
    memory           = 512
    entryPoint       = local.entryPoint
    command          = ["celery -A tasks worker --loglevel=INFO"]
    secrets          = local.secrets
    environment      = local.environment
    logConfiguration = local.logConfiguration
    }, {
    name             = "web"
    essential        = true
    image            = local.image
    cpu              = 10
    memory           = 512
    entryPoint       = local.entryPoint
    command          = ["gunicorn --bind 0.0.0.0:${var.port} wsgi:app"]
    secrets          = local.secrets
    environment      = local.environment
    logConfiguration = local.logConfiguration
    },
  ])

  execution_role_arn = aws_iam_role.email_server_task_execution_role.arn

  # minimum values for Fargate containers
  cpu                      = 256
  memory                   = 512
  requires_compatibilities = ["FARGATE"]

  # required for Fargate containers
  network_mode = "awsvpc"
}

resource "aws_ecs_cluster" "email_server" {
  name = "email-server"
}

resource "aws_ecs_service" "email_server" {
  name            = "email-server"
  task_definition = aws_ecs_task_definition.email_server.arn
  launch_type     = "FARGATE"
  cluster         = aws_ecs_cluster.email_server.id
  desired_count   = 1

  network_configuration {
    assign_public_ip = false

    security_groups = [
      aws_security_group.egress_all.id,
      aws_security_group.ingress_api.id,
    ]

    subnets = [
      aws_subnet.private_a.id,
      aws_subnet.private_b.id,
    ]
  }
}

# the role under which ECS will execute our task
resource "aws_iam_role" "email_server_task_execution_role" {
  name               = "email_server_task_execution_role"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_assume_role.json
}

data "aws_iam_policy_document" "ecs_task_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

# prefer not to hardcode an ARN in our Terraform, but since this is an
# AWS-managed policy, it's ok
data "aws_iam_policy" "ecs_task_execution_role" {
  arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# attach the above policy to the execution role
resource "aws_iam_role_policy_attachment" "ecs_task_execution_role" {
  role       = aws_iam_role.email_server_task_execution_role.name
  policy_arn = data.aws_iam_policy.ecs_task_execution_role.arn
}

data "aws_iam_policy" "ecs_task_secrets_role" {
  arn = "arn:aws:iam::aws:policy/SecretsManagerReadWrite"
}

resource "aws_iam_role_policy_attachment" "ecs_task_secrets_role" {
  role       = aws_iam_role.email_server_task_execution_role.name
  policy_arn = data.aws_iam_policy.ecs_task_secrets_role.arn
}
