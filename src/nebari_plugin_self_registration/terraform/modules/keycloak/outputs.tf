output "config" {
  description = "configuration credentials for Keyloak client"
  value = {
    client_id     = keycloak_openid_client.this.client_id
    client_secret = keycloak_openid_client.this.client_secret
  }
  sensitive = true
}