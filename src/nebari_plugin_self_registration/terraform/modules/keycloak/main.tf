locals {
}

resource "keycloak_openid_client" "this" {
  realm_id                     = var.realm_id
  name                         = var.client_id
  client_id                    = var.client_id
  access_type                  = "CONFIDENTIAL"
  base_url                     = var.base_url
  enabled                      = true
  service_accounts_enabled     = true
}

# Get manage-users role via data and assign it to registration client service account
data "keycloak_openid_client" "realm_management" {
  realm_id  = var.realm_id
  client_id = "realm-management"
}

data "keycloak_role" "manage_users" {
  realm_id  = var.realm_id
  client_id = data.keycloak_openid_client.realm_management.id
  name      = "manage-users"
}

resource "keycloak_openid_client_service_account_role" "registration_service_account_role" {
  realm_id                = var.realm_id
  service_account_user_id = keycloak_openid_client.this.service_account_user_id
   # Need to source as data?
  client_id               = data.keycloak_openid_client.realm_management.id
  role                    = data.keycloak_role.manage_users.name
}
