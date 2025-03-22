# README.md - Titan OS Infrastructure Take-Home Test

## Overview
Welcome to the Titan OS Infrastructure Take-Home Test! The purpose of this test is to assess how you approach deploying an application into a Kubernetes cluster. This document outlines the solution, including the application, Helm chart components, deployment instructions, and system architecture for an AWS-based deployment.

---

## 1. Application Overview

### Functionality
The application is a simple HTTP-based service that allows users to store and retrieve birthdays. It exposes two APIs:

1. **Save/Update User Birthday**
   - **Request:** `PUT /hello/<username>`
   - **Payload:** `{ "dateOfBirth": "YYYY-MM-DD" }`
   - **Response:** `204 No Content`
   - **Validation:**
     - Username must contain only letters.
     - Date of birth must be in the past.

2. **Retrieve Birthday Message**
   - **Request:** `GET /hello/<username>`
   - **Response:** `200 OK`
   - **Response Examples:**
     - If the birthday is in N days: `{ "message": "Hello, <username>! Your birthday is in N day(s)" }`
     - If the birthday is today: `{ "message": "Hello, <username>! Happy birthday!" }`

### Technology Stack
- **Language:** Python (Flask) / Node.js
- **Database:** MySQL
- **Containerization:** Docker
- **Orchestration:** Kubernetes (Minikube/K3s)

---

## 2. Helm Chart Components
To deploy the application using Helm, the following components are included:

- **Deployment**: Defines the application’s pods and their configurations.
- **Service**: Exposes the application within the Kubernetes cluster.
- **Ingress** (if applicable): Manages external access to the application.
- **ConfigMap**: Stores configuration settings.
- **Secret**: Stores sensitive information (e.g., database credentials).
- **PersistentVolumeClaim** (if required): Ensures database persistence.
- **Values.yaml**: Allows customization of configurations.

---

## 3. Local Deployment (Minikube/K3s)

### Prerequisites
- Docker installed
- Minikube or K3s installed
- Helm installed

### Steps
1. **Build and tag the application image:**  
   ```bash
   docker build -t birthday-app .
   ```
2. **Start Minikube/K3s:**  
   ```bash
   minikube start
   ```
3. **Load the Docker image into Minikube:**  
   ```bash
   minikube image load birthday-app
   ```
4. **Deploy using Helm:**  
   ```bash
   helm install birthday-app ./helm-chart
   ```
5. **Verify deployment:**  
   ```bash
   kubectl get pods
   kubectl get svc
   ```
6. **Access the application:**  
   ```bash
   minikube service birthday-app --url
   ```

---

## 4. AWS Deployment Architecture

### System Design Considerations
Given the high criticality and usage of the application, the AWS deployment will include:

- **Elastic Load Balancer (ALB)**: Distributes traffic.
- **Amazon EKS (Kubernetes Cluster)**: Manages containerized workloads.
- **Amazon RDS (MySQL)**: Provides a managed database.
- **Auto Scaling Group**: Ensures high availability.
- **CloudWatch & Prometheus**: Monitors performance.
- **Secrets Manager**: Stores sensitive credentials.

### AWS Deployment Steps
1. **Create an EKS cluster:**  
   ```bash
   eksctl create cluster --name birthday-cluster --region us-east-1
   ```
2. **Deploy the Helm chart:**  
   ```bash
   helm install birthday-app ./helm-chart --set image.repository=<ECR-Repo>
   ```
3. **Set up an external ALB using AWS Load Balancer Controller.**
4. **Configure RDS for database storage and connect it to the application.**

---

## 5. System Diagram

![AWS Infrastructure Diagram](./images/infra.png)

---

## 6. Repository Structure
```
📂 titan-os-takehome
 ├── 📂 app                  # Application source code
 ├── 📂 helm-chart           # Helm chart for deployment
 ├── 📂 docs                 # System diagram and documentation
 ├── Dockerfile              # Docker build file
 ├── README.md               # Instructions and overview
 ├── values.yaml             # Helm values configuration
```

---

## 7. Conclusion
This project demonstrates deploying a simple birthday API service using Kubernetes. The solution is designed for both local and cloud environments, ensuring scalability and resilience. The AWS deployment plan includes all necessary components to handle high traffic efficiently.



