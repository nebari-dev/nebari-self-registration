output "config" {
  description = "configuration credentials for connecting to openid client"
  value = {
    client_id     = keycloak_openid_client.this.client_id
    client_secret = keycloak_openid_client.this.client_secret
    signing_key   = local.signing_key

    issuer_url    = "${var.external_url}realms/${var.realm_id}"
    discovery_url = "${var.external_url}realms/${var.realm_id}/.well-known/openid-configuration"
    auth_url      = "${var.external_url}realms/${var.realm_id}/protocol/openid-connect/auth"
    token_url     = "${var.external_url}realms/${var.realm_id}/protocol/openid-connect/token"
    jwks_url      = "${var.external_url}realms/${var.realm_id}/protocol/openid-connect/certs"
    logout_url    = "${var.external_url}realms/${var.realm_id}/protocol/openid-connect/logout"
    userinfo_url  = "${var.external_url}realms/${var.realm_id}/protocol/openid-connect/userinfo"
  }
  sensitive = true
}