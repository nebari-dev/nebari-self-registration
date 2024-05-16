import datetime
import logging
import os
import yaml

from keycloak import KeycloakAdmin, KeycloakOpenIDConnection

log_level = os.environ.get("LOG_LEVEL", "info")

file_path = os.environ.get("KEYCLOAK_CONFIG_PATH", "/mnt/config.yaml")
with open(file_path, "r") as file:
    config = yaml.safe_load(file)

logging.basicConfig(format='%(asctime)s | %(levelname)-8s | %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.getLevelName(log_level.upper()))

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def run():
    try:
        keycloak_connection = KeycloakOpenIDConnection(
            server_url=config["keycloak"]["server_url"],
            realm_name=config["keycloak"]["realm_name"],
            client_id=config["keycloak"]["client_id"],
            client_secret_key=config["keycloak"]["client_secret"],
            user_realm_name=config["keycloak"]["realm_name"],
            verify=True,
        )

        keycloak_admin = KeycloakAdmin(connection=keycloak_connection)
    except Exception as e:
        logger.error(f"Failed to initialize Keycloak client, error {e}")
        exit(1)

    try:
        logger.info(
            f"Checking Keycloak ({keycloak_admin.connection.server_url}) for active account passed expiration..."
        )
        expired_users = check_expired_users(keycloak_admin)
        if not expired_users:
            logger.info("No expired users found, exiting")
            return

        for u in expired_users:
            disable_user(keycloak_admin, u)

        logger.info("Done")

    except Exception as e:
        logger.error(f"Failed to check expired Keycloak users, error {e}")
        exit(1)


def check_expired_users(keycloak_admin):
    page_num = 0
    page_size = 100

    now_utc = datetime.datetime.now(datetime.UTC)

    result = []

    while True:
        users = []

        try:
            users = keycloak_admin.get_users(
                {
                    "enabled": True,
                    "first": page_num * page_size,
                    "max": page_size,
                }
            )
        except Exception as e:
            logger.error(f"Failed to get Keycloak users, page {page_num}, size {page_size}, error {e}")
            break

        if len(users) == 0:
            logger.debug(f"No users found, page {page_num}, size {page_size}")
            break

        for u in users:
            try:
                if u.get("attributes") and len(u["attributes"].get("account_expiration_date", [])) > 0:
                    account_expiration_date_utc = datetime.datetime.strptime(
                        u["attributes"]["account_expiration_date"][0], DATE_FORMAT
                    ).replace(tzinfo=datetime.timezone.utc)
                    if account_expiration_date_utc < now_utc:
                        logger.debug(f"Expired user found {u['username']}")
                        result.append(u)
                    else:
                        logger.info(f"User {u['username']} still valid, {account_expiration_date_utc}")
                else:
                    logger.debug(f"User {u['username']} missing account_expiration_date attribute, ignoring")
            except Exception as e:
                logger.error(f"Failed to process user {u['username']}, error {e}")

        page_num += 1

    return result


def disable_user(keycloak_admin, user):
    logger.warning(f"Disabling user {user['username']}")

    try:
        user["enabled"] = False
        user["attributes"]["disabled_by"] = os.environ.get("JOB_NAME", os.environ.get("HOSTNAME", "cronjob"))
        user["attributes"]["disabled_on"] = datetime.datetime.now(datetime.UTC).strftime(DATE_FORMAT)
        keycloak_admin.update_user(user_id=user["id"], payload=user)
        return True
    except Exception as e:
        logger.error(f"Failed to disable user {user['username']}, error {e}")
        return False


if __name__ == "__main__":
    run()
