variable "chart_name" {
  description = "Name for self registration chart and its namespaced resources."
  type        = string
}

variable "create_namespace" {
  type = bool
}

variable "ingress_host" {
  description = "DNS name for Traefik host"
  type        = string
}

variable "keycloak_config" {
  description = "Keycloak configuration settings"
  type        = map(string)
}

variable "namespace" {
  type = string
}

variable "self_registration_sa_name" {
  description = "Name of K8S service account for Self Registration app workloads"
  type        = string
}

variable "overrides" {
  type    = map(any)
  default = {}
}