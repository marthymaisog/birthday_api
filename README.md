
# Birthday API Application

A simple Kubernetes-based application that manages user birthdays through REST APIs, deployed using Helm on Minikube.

## Features

- Create/update user birthdays via PUT requests
- Get birthday countdown messages via GET requests
- Persistent SQLite storage
- Health checks for Kubernetes
- Helm chart for easy deployment

## Prerequisites

- [Minikube](https://minikube.sigs.k8s.io/docs/start/)
- [Helm](https://helm.sh/docs/intro/install/)
- [Docker](https://docs.docker.com/get-docker/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)

## Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/marthymaisog/titanos.git
cd titanos/php-birthday-app
```

### 2. Start Minikube Cluster
```bash
minikube start
eval $(minikube docker-env)  # Use Minikube's Docker daemon
```

### 3. Build & Deploy
```bash
docker build -t birthday-app-python:latest .
helm install birthday-app-python ./helm-chart
kubectl port-forward svc/birthday-app-python-service 8080:5000
```

## API Documentation

| Endpoint        | Method | Description                | Example Request Body             |
|-----------------|--------|----------------------------|----------------------------------|
| /hello/<name>   | PUT    | Create/update birthday     | {"dateOfBirth": "1990-05-15"}    |
| /hello/<name>   | GET    | Get birthday message       | -                                |
| /health         | GET    | Service health check       | -                                |

## Troubleshooting Guide

### Common Errors & Fixes

#### Image Build Failures
- Rebuild with clean cache:
  ```bash
  docker build --no-cache -t birthday-app-python:latest .
  ```

#### PVC Issues
- Force delete PVC:
  ```bash
  kubectl patch pvc birthday-app-python-pvc -p '{"metadata":{"finalizers":null}}'
  kubectl delete pvc birthday-app-python-pvc --force
  ```

#### Full Cleanup Command
```bash
helm uninstall birthday-app-python
kubectl delete svc birthday-app-python-service
kubectl delete secret -l owner=helm
```

#### Reset Minikube Networking
```bash
minikube ssh -- sudo systemctl restart docker
minikube delete && minikube start
```

### Upgrade Deployment
```bash
docker build -t birthday-app-python:latest .
helm upgrade birthday-app-python ./helm-chart
```

### Database Operations

#### Export Database
```bash
kubectl exec deployment/birthday-app-python -- sqlite3 /data/birthdays.db .dump > backup.sql
```

#### Import Database
```bash
kubectl exec -i deployment/birthday-app-python -- sqlite3 /data/birthdays.db < backup.sql
```

### Clean Up
```bash
helm uninstall birthday-app-python
kubectl delete pvc birthday-app-python-pvc
minikube stop
```

## Helm Chart Structure

The **Helm Chart** for this application (`./helm-chart`) includes the following key components:

### 1. **Chart.yaml**
Defines metadata about the Helm chart (name, version, description).

```yaml
name: birthday-app-python
version: 0.1.0
description: A simple application to manage user birthdays.
```

### 2. **values.yaml**
Contains configuration parameters for the application (e.g., container image version, resource limits, service type).

```yaml
image:
  repository: birthday-app-python
  tag: latest

replicas: 2

service:
  type: LoadBalancer
```

### 3. **Templates/**  
Contains Kubernetes manifests that Helm will dynamically populate with values from `values.yaml`. Common templates include:

#### **deployment.yaml**
Defines the Kubernetes deployment for the application.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: birthday-app-python
spec:
  replicas: {{ .Values.replicas }}
  selector:
    matchLabels:
      app: birthday-app-python
  template:
    metadata:
      labels:
        app: birthday-app-python
    spec:
      containers:
        - name: birthday-app-python
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          ports:
            - containerPort: 5000
```

#### **service.yaml**
Defines how the application is exposed (internally or externally).

```yaml
apiVersion: v1
kind: Service
metadata:
  name: birthday-app-python-service
spec:
  selector:
    app: birthday-app-python
  ports:
    - protocol: TCP
      port: 80
      targetPort: 5000
  type: {{ .Values.service.type }}
```

#### **ingress.yaml** (Optional)
Used to route external HTTP/HTTPS traffic to the application. Requires an Ingress Controller (e.g., Nginx, Traefik).

#### **configmap.yaml** (Optional)
Defines non-sensitive configuration values for the application.

#### **secret.yaml** (Optional)
Stores sensitive information like API keys or database credentials.

### 4. **helpers.tpl**
Contains reusable Helm template snippets.

```yaml
{{- define "birthday-app-python.labels" -}}
app: birthday-app-python
{{- end -}}
```

### 5. **values-override.yaml** (Optional)
Override default values for different environments (e.g., production, staging).

---

## Helm Commands

- **Install the application**:
  ```bash
  helm install birthday-app-python ./helm-chart
  ```

- **Upgrade the application**:
  ```bash
  helm upgrade birthday-app-python ./helm-chart
  ```

- **Uninstall the application**:
  ```bash
  helm uninstall birthday-app-python
  ```

## Additional Resources

- **Helm Chart**: [GitHub Link](https://github.com/marthymaisog/titanos/tree/main/php-birthday-app/helm-chart)
- **AWS Diagram**: [GitHub Link](https://github.com/marthymaisog/titanos/blob/main/AWS_Diagram.md)

---
