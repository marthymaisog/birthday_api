# Docker and Minikube Installation Guide

This guide provides step-by-step instructions for installing Docker and Minikube on different operating systems.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Installing Docker](#installing-docker)
  - [Windows](#docker-on-windows)
  - [macOS](#docker-on-macos)
  - [Linux](#docker-on-linux)
- [Installing Minikube](#installing-minikube)
  - [Windows](#minikube-on-windows)
  - [macOS](#minikube-on-macos)
  - [Linux](#minikube-on-linux)
- [Verifying Installation](#verifying-installation)
- [Basic Usage](#basic-usage)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements
- **Windows**: Windows 10 64-bit (Build 18362+) or Windows 11
- **macOS**: macOS 10.15 Catalina or newer
- **Linux**: Any modern distribution with kernel 3.10+
- At least 2GB of RAM (4GB recommended)
- 20GB of free disk space
- CPU with virtualization support (Intel VT-x/AMD-v)

### Enable Virtualization
Ensure virtualization is enabled in your BIOS/UEFI settings.

## Installing Docker

### Docker on Windows

1. **Install Docker Desktop**:
   - Download Docker Desktop from [Docker's official website](https://www.docker.com/products/docker-desktop)
   - Run the installer and follow the prompts
   - Ensure WSL 2 is selected during installation (recommended)

2. **Post-Installation Steps**:
   - Launch Docker Desktop
   - Wait for the service to start (indicator turns green)
   - Open a command prompt and verify with `docker --version`

### Docker on macOS

1. **Install Docker Desktop**:
   - Download Docker Desktop for Mac from [Docker's official website](https://www.docker.com/products/docker-desktop)
   - Drag the Docker icon to the Applications folder
   - Launch Docker from Applications

2. **Post-Installation Steps**:
   - Allow Docker to complete its startup process
   - Verify installation with `docker --version` in Terminal

### Docker on Linux

#### Ubuntu/Debian:

```bash
# Uninstall old versions
sudo apt-get remove docker docker-engine docker.io containerd runc

# Set up the repository
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg lsb-release

# Add Docker's official GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set up the repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add your user to the docker group (to run Docker without sudo)
sudo usermod -aG docker $USER
```

#### Fedora/CentOS/RHEL:

```bash
# Remove old versions
sudo yum remove docker docker-client docker-client-latest docker-common docker-latest docker-latest-logrotate docker-logrotate docker-engine

# Set up the repository
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo

# Install Docker Engine
sudo yum install docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker

# Add your user to the docker group
sudo usermod -aG docker $USER
```

## Installing Minikube

### Minikube on Windows

1. **Install via PowerShell** (Run as Administrator):
   ```powershell
   New-Item -Path 'C:\Program Files\Minikube' -ItemType Directory -Force
   Invoke-WebRequest -OutFile 'C:\Program Files\Minikube\minikube.exe' -Uri 'https://github.com/kubernetes/minikube/releases/latest/download/minikube-windows-amd64.exe'
   Add-Content -Path $env:USERPROFILE\\.bash_profile -Value 'export PATH="$PATH:/c/Program Files/Minikube"'
   ```

2. **Manually add to PATH**:
   - Right-click on "This PC" > Properties > Advanced System Settings > Environment Variables
   - Edit the PATH variable and add `C:\Program Files\Minikube`

### Minikube on macOS

1. **Using Homebrew**:
   ```bash
   brew install minikube
   ```

2. **Manual download**:
   ```bash
   curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-darwin-amd64
   sudo install minikube-darwin-amd64 /usr/local/bin/minikube
   ```

### Minikube on Linux

1. **Using binary download**:
   ```bash
   curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
   sudo install minikube-linux-amd64 /usr/local/bin/minikube
   ```

2. **Install kubectl** (if not already installed):
   ```bash
   curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
   sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
   ```

## Verifying Installation

### Verify Docker
```bash
docker --version
docker run hello-world
```

### Verify Minikube
```bash
minikube version
```

### Start Minikube
```bash
minikube start --driver=docker
```
Note: You can also use other drivers like `virtualbox`, `hyperv`, `kvm2` depending on your system configuration.

### Verify Kubernetes
```bash
kubectl get nodes
minikube status
```

## Basic Usage

### Docker Commands
```bash
# List running containers
docker ps

# List all containers (including stopped ones)
docker ps -a

# Pull an image
docker pull nginx

# Run a container
docker run -d -p 8080:80 nginx

# Stop a container
docker stop <container_id>

# Remove a container
docker rm <container_id>
```

### Minikube Commands
```bash
# Start Minikube
minikube start

# Stop Minikube
minikube stop

# Delete Minikube cluster
minikube delete

# Access Minikube dashboard
minikube dashboard

# SSH into Minikube VM
minikube ssh

# Get Minikube IP
minikube ip
```

### Kubernetes Commands
```bash
# View all resources
kubectl get all

# Deploy an application
kubectl create deployment nginx --image=nginx

# Expose deployment as a service
kubectl expose deployment nginx --port=80 --type=NodePort

# Access the service
minikube service nginx
```

## Troubleshooting

### Common Docker Issues

1. **Docker service not running**:
   ```bash
   # Windows/Mac
   Restart Docker Desktop

   # Linux
   sudo systemctl restart docker
   ```

2. **Permission denied**:
   ```bash
   # Add user to docker group
   sudo usermod -aG docker $USER
   # Log out and log back in
   ```

3. **Disk space issue**:
   ```bash
   # Clean up unused containers, networks, images
   docker system prune -a
   ```

### Common Minikube Issues

1. **Minikube won't start**:
   ```bash
   minikube delete
   minikube start --driver=docker
   ```

2. **VM driver issues**:
   - Try a different driver: `minikube start --driver=virtualbox` or `minikube start --driver=hyperv`

3. **Insufficient resources**:
   ```bash
   minikube start --memory=4096 --cpus=2
   ```

4. **Connection issues with kubectl**:
   ```bash
   minikube update-context
   ```

For additional help, refer to:
- [Docker documentation](https://docs.docker.com/)
- [Minikube documentation](https://minikube.sigs.k8s.io/docs/)
- [Kubernetes documentation](https://kubernetes.io/docs/home/)
