locals {
  signing_key = (var.signing_key_ref == null
    ? random_password.signing_key[0].result
  : one([for e in data.kubernetes_resource.signing_key[0].object.spec.template.spec.containers[0].env : e.value if e.name == "SECRET"]))
}

resource "keycloak_openid_client" "this" {
  realm_id                     = var.realm_id
  name                         = var.client_id
  client_id                    = var.client_id
  access_type                  = "CONFIDENTIAL"
  base_url                     = var.base_url
  valid_redirect_uris          = var.valid_redirect_uris
  enabled                      = true
  standard_flow_enabled        = true
  direct_access_grants_enabled = false
  web_origins                  = ["+"]
}

resource "keycloak_openid_user_client_role_protocol_mapper" "this" {
  realm_id   = var.realm_id
  client_id  = keycloak_openid_client.this.id
  name       = "user-client-role-mapper"
  claim_name = "roles"

  claim_value_type    = "String"
  multivalued         = true
  add_to_id_token     = true
  add_to_access_token = true
  add_to_userinfo     = true
}

resource "keycloak_openid_group_membership_protocol_mapper" "this" {
  realm_id   = var.realm_id
  client_id  = keycloak_openid_client.this.id
  name       = "group-membership-mapper"
  claim_name = "groups"

  full_path           = true
  add_to_id_token     = true
  add_to_access_token = true
  add_to_userinfo     = true
}

data "kubernetes_resource" "signing_key" {
  count = var.signing_key_ref == null ? 0 : 1

  api_version = "apps/v1"
  kind        = var.signing_key_ref.kind == null ? "Deployment" : var.signing_key_ref.kind

  metadata {
    namespace = var.signing_key_ref.namespace
    name      = var.signing_key_ref.name
  }
}

resource "random_password" "signing_key" {
  count = var.signing_key_ref == null ? 1 : 0

  length  = 32
  special = false
}
