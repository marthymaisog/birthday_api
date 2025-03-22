
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
apiVersion: v2
name: birthday-app-python
description: Birthday reminder application in Python
version: 0.2.0
appVersion: "2.0"
```

### 2. **values.yaml**
Contains configuration parameters for the application (e.g., container image version, resource limits, service type).

```yaml
replicaCount: 1
image:
  repository: birthday-app-python
  tag: latest
  pullPolicy: IfNotPresent
service:
  type: ClusterIP
  port: 5000
persistence:
  enabled: true
  accessMode: ReadWriteOnce
  storageSize: 1Gi
  mountPath: /data
resources:
  requests:
    memory: "128Mi"
    cpu: "100m"
  limits:
    memory: "256Mi"
    cpu: "200m"
```

### 3. **Templates/**  
Contains Kubernetes manifests that Helm will dynamically populate with values from `values.yaml`. Common templates include:

#### **deployment.yaml**
Defines the Kubernetes deployment for the application.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Chart.Name }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      app: {{ .Chart.Name }}
  template:
    metadata:
      labels:
        app: {{ .Chart.Name }}
    spec:
      securityContext:
        fsGroup: 1000
        runAsUser: 1000
        runAsGroup: 1000
      containers:
      - name: {{ .Chart.Name }}
        image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
        imagePullPolicy: {{ .Values.image.pullPolicy }}
        ports:
        - containerPort: 5000
        volumeMounts:
        - name: data
          mountPath: {{ .Values.persistence.mountPath }}
        resources:
          {{- toYaml .Values.resources | nindent 12 }}
        livenessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: {{ .Chart.Name }}-pvc
```

#### **service.yaml**
Defines how the application is exposed (internally or externally).

```yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ .Chart.Name }}-service
spec:
  type: {{ .Values.service.type }}
  ports:
  - port: {{ .Values.service.port }}
    targetPort: 5000
  selector:
    app: {{ .Chart.Name }}
```

### 4. **pvc.yaml**
PersistentVolumeClaim (PVC), which is used to request persistent storage.

```yaml
{{- if .Values.persistence.enabled }}
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: {{ .Chart.Name }}-pvc
spec:
  accessModes:
    - {{ .Values.persistence.accessMode }}
  resources:
    requests:
      storage: {{ .Values.persistence.storageSize }}
{{- end }}
```

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

- **OUTPUT**:
  
  ![Output](./images/birthday.png)
  