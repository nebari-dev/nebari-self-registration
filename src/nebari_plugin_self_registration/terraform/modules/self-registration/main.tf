locals {
  affinity = var.affinity != null && lookup(var.affinity, "enabled", false) ? {
    enabled = true
    selector = try(
      { for k in ["default", "app", "job"] : k => length(var.affinity.selector[k]) > 0 ? var.affinity.selector[k] : var.affinity.selector.default },
      {
        app = var.affinity.selector
        job  = var.affinity.selector
      },
    )
    } : {
    enabled  = false
    selector = null
  }

  affinity_selector_key = {
    aws = "eks.amazonaws.com/nodegroup"
    gcp = "cloud.google.com/gke-nodepool"
  }
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
      affinity = local.affinity.enabled ? {
        nodeAffinity = {
          requiredDuringSchedulingIgnoredDuringExecution = {
            nodeSelectorTerms = [
              {
                matchExpressions = [
                  {
                    key      = local.affinity_selector_key[var.cloud_provider]
                    operator = "In"
                    values   = [local.affinity.selector.app]
                  }
                ]
              }
            ]
          }
        }
      } : {}
      job = {
        affinity = local.affinity.enabled ? {
          nodeAffinity = {
            requiredDuringSchedulingIgnoredDuringExecution = {
              nodeSelectorTerms = [
                {
                  matchExpressions = [
                    {
                      key      = local.affinity_selector_key[var.cloud_provider]
                      operator = "In"
                      values   = [local.affinity.selector.job]
                    }
                  ]
                }
              ]
            }
          }
        } : {}
      }
      serviceAccount = {
        name = var.self_registration_sa_name
      }
      app_configuration = {
        coupons                 = var.coupons
        approved_domains        = var.approved_domains
        account_expiration_days = var.account_expiration_days
        registration_group      = var.registration_group
        registration_message    = var.registration_message
        keycloak = {
          server_url    = var.keycloak_base_url
          realm_name    = var.realm_id
          client_id     = var.keycloak_config["client_id"]
          client_secret = var.keycloak_config["client_secret"]
        }
        theme                   = var.theme
      }
      env = [
      ]
    }),
    yamlencode(var.overrides),
  ]
}