locals {
  self_registration_sa_name = "${var.chart_name}-sa"
}

module "keycloak" {
  source = "./modules/keycloak"

  realm_id            = var.realm_id
  client_id           = var.client_id
  base_url            = var.base_url
  external_url        = var.external_url
  valid_redirect_uris = var.valid_redirect_uris
  signing_key_ref     = var.signing_key_ref
}

module "self-registration" {
  source = "./modules/self-registration"

  chart_name                = var.chart_name
  create_namespace          = var.create_namespace
  ingress_host              = var.ingress_host
  self_registration_sa_name = local.self_registration_sa_name
  namespace                 = var.namespace
  keycloak_config           = module.keycloak.config
  overrides                 = var.overrides
}