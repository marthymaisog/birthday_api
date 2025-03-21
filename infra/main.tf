# Configure the Minikube provider
provider "kubernetes" {
  config_path = "~/.kube/config"
}

# Create a namespace for the application
resource "kubernetes_namespace" "hello_app_namespace" {
  metadata {
    name = "hello-app-namespace"
  }
}

# Create a deployment for the application
resource "kubernetes_deployment" "hello_app_deployment" {
  metadata {
    name      = "hello-app-deployment"
    namespace = kubernetes_namespace.hello_app_namespace.metadata[0].name
  }

  spec {
    replicas = 1

    selector {
      match_labels = {
        app = "hello-app"
      }
    }

    template {
      metadata {
        labels = {
          app = "hello-app"
        }
      }

      spec {
        container {
          image = "hello-app:latest"
          name  = "hello-app-container"

          port {
            container_port = 80
          }
        }
      }
    }
  }
}

# Create a service for the application
resource "kubernetes_service" "hello_app_service" {
  metadata {
    name      = "hello-app-service"
    namespace = kubernetes_namespace.hello_app_namespace.metadata[0].name
  }

  spec {
    selector = {
      app = "hello-app"
    }

    port {
      port        = 80
      target_port = 80
    }

    type = "LoadBalancer"
  }
}

# Create a persistent volume claim for the database
resource "kubernetes_persistent_volume_claim" "hello_app_pvc" {
  metadata {
    name      = "hello-app-pvc"
    namespace = kubernetes_namespace.hello_app_namespace.metadata[0].name
  }

  spec {
    access_modes = ["ReadWriteOnce"]

    resources {
      requests = {
        storage = "1Gi"
      }
    }
  }
}

# Create a deployment for the database
resource "kubernetes_deployment" "hello_app_db_deployment" {
  metadata {
    name      = "hello-app-db-deployment"
    namespace = kubernetes_namespace.hello_app_namespace.metadata[0].name
  }

  spec {
    replicas = 1

    selector {
      match_labels = {
        app = "hello-app-db"
      }
    }

    template {
      metadata {
        labels = {
          app = "hello-app-db"
        }
      }

      spec {
        container {
          image = "postgres:latest"
          name  = "hello-app-db-container"

          port {
            container_port = 5432
          }

          env {
            name  = "POSTGRES_USER"
            value = "helloappuser"
          }

          env {
            name  = "POSTGRES_PASSWORD"
            value = "helloapppassword"
          }

          env {
            name  = "POSTGRES_DB"
            value = "helloappdb"
          }

          volume_mount {
            name       = "hello-app-pvc"
            mount_path = "/var/lib/postgresql/data"
          }
        }

        volume {
          name = "hello-app-pvc"

          persistent_volume_claim {
            claim_name = kubernetes_persistent_volume_claim.hello_app_pvc.metadata[0].name
          }
        }
      }
    }
  }
}

# Create a service for the database
resource "kubernetes_service" "hello_app_db_service" {
  metadata {
    name      = "hello-app-db-service"
    namespace = kubernetes_namespace.hello_app_namespace.metadata[0].name
  }

  spec {
    selector = {
      app = "hello-app-db"
    }

    port {
      port        = 5432
      target_port = 5432
    }

    type = "ClusterIP"
  }
}
