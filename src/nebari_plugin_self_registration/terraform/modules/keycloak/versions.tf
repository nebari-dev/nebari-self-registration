terraform {
  required_providers {
    keycloak = {
      source  = "mrparkers/keycloak"
      version = "4.3.1"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = ">= 2.22.0"
    }
  }
  required_version = ">= 1.0"
}

provider "keycloak" {
  tls_insecure_skip_verify = true
  base_path                = "/auth"
}
