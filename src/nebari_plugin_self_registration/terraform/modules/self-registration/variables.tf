variable "chart_name" {
  description = "Name for self registration chart and its namespaced resources."
  type        = string
}

variable "account_expiration_days" {
  description = "Days a self-registered account remains active before expiring."
  type        = number
}

variable "approved_domains" {
  description = "Approved email domains for user self registration"
  type        = list(string)
}

variable "coupons" {
  description = "Valid coupons for user self registration"
  type        = list(string)
}

variable "create_namespace" {
  type = bool
}

variable "ingress_host" {
  description = "DNS name for Traefik host"
  type        = string
}

variable "keycloak_base_url" {
  description = "Base URL for KeycloakAdmin"
  type        = string
}

variable "keycloak_config" {
  description = "Keycloak configuration settings"
  type        = map(string)
}

variable "namespace" {
  type = string
}

variable "realm_id" {
  description = "Keycloak realm_id"
  type        = string
}

variable "registration_group" {
  description = "Name of Keycloak group to add registering users"
  type        = string
}

variable "registration_message" {
  description = "Custom message to display to registering users"
  type        = string
  default     = ""
}

variable "self_registration_sa_name" {
  description = "Name of K8S service account for Self Registration app workloads"
  type        = string
}

variable "overrides" {
  type    = map(any)
  default = {}
}

variable "affinity" {
  type = object({
    enabled  = optional(bool, true)
    selector = optional(any, "general")
  })

  default = {
    enabled  = false
    selector = "general"
  }

  validation {
    condition     = can(tostring(var.affinity.selector)) || (can(var.affinity.selector.default) && length(try(var.affinity.selector.default, "")) > 0)
    error_message = "\"affinity.selector\" argument must be a string or object { default, app, job }"
  }
}


variable "cloud_provider" {
  type = string
}

variable "theme" {
  description = "Theme configured in theme.jupyterhub"
  type        = map(any)
  default     = {}
}
