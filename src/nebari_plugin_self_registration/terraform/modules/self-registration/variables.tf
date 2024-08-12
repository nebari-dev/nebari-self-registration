variable "chart_name" {
  description = "Name for self registration chart and its namespaced resources."
  type        = string
}

variable "coupons" {
  description = "Coupon configuration for user self registration"
  type = map(object({
    account_expiration_days = number
    approved_domains        = list(string)
    registration_groups     = list(string)
  }))
  default = {}
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
