
# AWS Infrastructure Diagram

![AWS Infrastructure Diagram](./images/infra.png)


# **Implementation**

## Components and Implemention using Terraform:

### **1. Global Layer (Edge Services)**
- **Amazon CloudFront - CDN for caching static assets and API responses at edge locations. Integrated with AWS WAF and Shield for DDoS protection.**:  
  ```terraform
  resource "aws_cloudfront_distribution" "cdn" {
    origin {
      domain_name = aws_alb.alb.dns_name
      origin_id   = "ALBOrigin"
    }
    enabled = true
    default_cache_behavior {
      target_origin_id       = "ALBOrigin"
      viewer_protocol_policy = "redirect-to-https"
    }
  }
  ```
- **Route 53 - DNS management with health checks for failover routing.**:  
  ```terraform
  resource "aws_route53_record" "dns" {
    zone_id = "your_zone_id"
    name    = "api.example.com"
    type    = "A"
    alias {
      name                   = aws_alb.alb.dns_name
      zone_id                = aws_alb.alb.zone_id
      evaluate_target_health = true
    }
  }
  ```

### **2. Regional Layer (VPC)**
- **VPC and Subnets - Public subnets for internet-facing components. Private subnets for internal resources. Multi-AZ deployment across 3 Availability Zones.**:
  ```terraform
  resource "aws_vpc" "main" {
    cidr_block = "10.0.0.0/16"
  }
  resource "aws_subnet" "public" {
    vpc_id = aws_vpc.main.id
    cidr_block = "10.0.1.0/24"
    map_public_ip_on_launch = true
  }
  resource "aws_subnet" "private" {
    vpc_id = aws_vpc.main.id
    cidr_block = "10.0.2.0/24"
  }
  ```

### **3. Compute & Orchestration**
- **Amazon EKS Cluster - Managed Kubernetes cluster in private subnets. Node groups with Auto Scaling Groups (ASG) for EC2 instances. Horizontal Pod Autoscaler (HPA) for dynamic scaling. IAM Roles for Service Accounts (IRSA) for secure AWS access.**:
  ```terraform
  resource "aws_eks_cluster" "eks" {
    name     = "titan-cluster"
    role_arn = aws_iam_role.eks_role.arn
    vpc_config {
      subnet_ids = [aws_subnet.private.id]
    }
  }
  ```
- **Application Load Balancer (ALB) - Routes traffic to EKS pods via Kubernetes Ingress. SSL termination using AWS Certificate Manager (ACM).**:
  ```terraform
  resource "aws_lb" "alb" {
    name               = "eks-alb"
    load_balancer_type = "application"
    security_groups    = [aws_security_group.alb_sg.id]
    subnets           = [aws_subnet.public.id]
  }
  ```

### **4. Data Layer**
- **Amazon Aurora (PostgreSQL) - Multi-AZ relational database with read replicas. Automated backups with point-in-time recovery.**
  ```terraform
  resource "aws_rds_cluster" "aurora" {
    cluster_identifier = "birthday-db"
    engine            = "aurora-postgresql"
    master_username   = "admin"
    master_password   = "securepassword"
    backup_retention_period = 7
  }
  ```
- **Amazon ElastiCache (Redis) - In-memory caching for high-throughput API requests**
  ```terraform
  resource "aws_elasticache_cluster" "cache" {
    cluster_id           = "titan-cache"
    engine              = "redis"
    node_type           = "cache.t3.micro"
    num_cache_nodes     = 1
  }
  ```

### **5. Security & Compliance**
- **Security Groups & Secrets  - Restrict traffic between layers (e.g., ALB → EKS, EKS → RDS).**
- **AWS Key Management Service (KMS) - Encrypts data at rest (RDS, EBS, ElastiCache).**
- **AWS Secrets Manager - Securely stores database credentials.**
  ```terraform
  resource "aws_secretsmanager_secret" "db_secret" {
    name = "db-credentials"
  }
  resource "aws_kms_key" "app_kms" {
  description             = "KMS key for encrypting RDS, EBS, and ElastiCache"
  enable_key_rotation     = true
  }

  resource "aws_kms_alias" "app_kms_alias" {
    name          = "alias/app-key"
    target_key_id = aws_kms_key.app_kms.id
  }
  ```

### **6. Monitoring & Operations**
- **Amazon CloudWatch -  Collects metrics/logs from EKS, ALB, RDS, and ElastiCache. Alarms for auto-scaling triggers.**
  ```terraform
  resource "aws_cloudwatch_log_group" "eks_logs" {
    name = "/aws/eks/titan-cluster"
  }
  ```

### **7. AWS X-Ray (Request Tracing for Microservices)**
- **AWS X-Ray -  AWS X-Ray helps trace requests between services in a Kubernetes-based application.**
  ```terraform
  resource "aws_xray_group" "app_tracing" {
    group_name = "app-tracing-group"
    filter_expression = "service(\"*app-service*\")"
  }

  resource "aws_iam_policy" "xray_policy" {
    name   = "xray-eks-policy"
    policy = jsonencode({
      Version = "2012-10-17",
      Statement = [
        {
          Effect = "Allow",
          Action = [
            "xray:PutTraceSegments",
            "xray:PutTelemetryRecords",
            "xray:GetSamplingRules",
            "xray:GetSamplingTargets"
          ],
          Resource = "*"
        }
      ]
    })
  }

  resource "aws_iam_role" "xray_role" {
    name = "xray-eks-role"
    assume_role_policy = jsonencode({
      Version = "2012-10-17",
      Statement = [{
        Effect = "Allow",
        Principal = { Service = "eks.amazonaws.com" },
        Action = "sts:AssumeRole"
      }]
    })
  }

  resource "aws_iam_role_policy_attachment" "xray_role_attach" {
    role       = aws_iam_role.xray_role.name
    policy_arn = aws_iam_policy.xray_policy.arn
  }
  ```

### **8. Prometheus & Grafana (Monitoring Kubernetes)**
- **ECR (Docker Registry)**
  ```terraform
  resource "helm_release" "prometheus" {
    name       = "prometheus"
    repository = "https://prometheus-community.github.io/helm-charts"
    chart      = "prometheus"

    set {
      name  = "server.persistentVolume.enabled"
      value = "true"
    }
  }

  resource "helm_release" "grafana" {
    name       = "grafana"
    repository = "https://grafana.github.io/helm-charts"
    chart      = "grafana"

    set {
      name  = "adminPassword"
      value = "super-secure-password"
    }
  }
  ```


### **9. CI/CD Pipeline**
- **ECR (Docker Registry) - Stores container images for EKS deployments.**
  ```terraform
  resource "aws_ecr_repository" "repo" {
    name = "birthday-app"
  }
  ```
- **CodePipeline & CodeBuild - Triggers builds on code commits (GitHub integration).**
  ```terraform
  resource "aws_codepipeline" "pipeline" {
    name = "birthday-app-pipeline"
    role_arn = aws_iam_role.pipeline_role.arn
  }
  ```
- **Helm Charts - Deploy updates to EKS via helm upgrade.**
  ```terraform
  provider "helm" {
    kubernetes {
      host                   = aws_eks_cluster.main.endpoint
      token                  = data.aws_eks_cluster_auth.main.token
      cluster_ca_certificate = base64decode(aws_eks_cluster.main.certificate_authority[0].data)
    }
  }

  resource "helm_release" "app" {
    name       = "birthday-app"
    repository = "repository = "oci://<aws_account_id>.dkr.ecr.<region>.amazonaws.com/my-helm-repo" ##OCI (Open Container Initiative) 
    chart      = "./helm-chart"

    set {
      name  = "image.repository"
      value = "<ECR-Repo-URL>"
    }

    set {
      name  = "service.type"
      value = "LoadBalancer"
    }

    depends_on = [aws_eks_cluster.main]
  }
  ```

### **10. Backup & Disaster Recovery**
- **RDS Snapshots - RDS snapshots and S3 buckets replicated to a secondary region.**
  ```terraform
  resource "aws_rds_cluster_snapshot" "snapshot" {
    db_cluster_identifier = aws_rds_cluster.aurora.id
    db_cluster_snapshot_identifier = "aurora-snapshot"
  }
  ```
- **S3 for Logs & Backups - Stores Terraform state, application logs, and database backups. Versioning enabled for rollbacks.**
  ```terraform
  resource "aws_s3_bucket" "logs" {
    bucket = "titan-logs"
  }
  ```
### Data Flow
```
User → CloudFront (cached response or SSL termination) → Route 53 → ALB.

ALB routes to EKS pods across AZs.

Pods query ElastiCache (cache layer) or Aurora (persistent data).

CI/CD updates trigger CodePipeline → ECR → EKS via Helm.

CloudWatch/X-Ray monitor performance; auto-scaling adjusts resources.
```

### Resilience Features
```
Multi-AZ Redundancy: All critical services (EKS, RDS, ElastiCache) span 3 AZs.

Auto-Scaling: Pods (HPA) and nodes (Cluster Autoscaler) scale based on load.

Immutable Infrastructure: Containerized deployments with rolling updates.

Backups: Daily RDS snapshots and continuous S3 versioning.

```

### Cost Optimization
```
Spot Instances: For non-critical EKS worker nodes.

Reserved Instances: For long-running RDS/Aurora databases.

Lifecycle Policies: Archive old S3 data to Glacier.
```
---

# This Terraform setup ensures a highly available and resilient AWS deployment 🚀

