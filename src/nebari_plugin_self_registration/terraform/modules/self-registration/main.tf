locals {
}

resource "kubernetes_namespace" "this" {
  count = var.create_namespace ? 1 : 0

  metadata {
    name = var.namespace
  }
}

resource "helm_release" "self_registration" {
  name      = var.chart_name
  chart     = "${path.module}/chart"
  namespace = var.create_namespace ? kubernetes_namespace.this[0].metadata[0].name : var.namespace

  values = [
    yamlencode({
      logLevel = "info"
      timeout  = "3600"
      ingress = {
        enabled = "true"
        host    = var.ingress_host
      }
      serviceAccount = {
        name = var.self_registration_sa_name
      }
      app_configuration = {
        coupons                 = var.coupons
        approved_domains        = var.approved_domains
        account_expiration_days = var.account_expiration_days
        registration_group      = var.registration_group
        keycloak = {
          server_url    = var.keycloak_base_url
          realm_name    = var.realm_id
          client_id     = var.keycloak_config["client_id"]
          client_secret = var.keycloak_config["client_secret"]
        }
      }
      env = [
      ]
    }),
    yamlencode(var.overrides),
  ]
}