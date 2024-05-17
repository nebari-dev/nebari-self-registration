import os
import random
import re
import string
from datetime import datetime, timedelta

import yaml
from fastapi import APIRouter, FastAPI, Form, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from keycloak import KeycloakAdmin, KeycloakConnectionError, KeycloakGetError
from theme import DEFAULT_THEME


class UserExistsException(Exception):
    pass


# Manual context URL.  Must be prepended to all paths in app and templates.
url_prefix = "/registration"

app = FastAPI()

app.mount(url_prefix + "/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

mount_path = "/mnt/config.yaml"
app_path = "/app/config.yaml"
if os.path.exists(mount_path):
    with open(mount_path) as file:
        config = yaml.safe_load(file)
elif os.path.exists(app_path):
    with open(app_path) as file:
        config = yaml.safe_load(file)
else:
    config = {}


def check_email_domain(email):
    approved_domains = config.get("approved_domains", [])
    for domain in approved_domains:
        # Replace wildcard with its regex equivalent
        pattern = domain.replace("*", ".*")
        if re.search(f"@{pattern}$", email):
            return True
    return False


def create_keycloak_user(email, expiration_days=7):
    # Random password generator
    def generate_random_password(length=12):
        characters = string.ascii_letters + string.digits + string.punctuation
        return "".join(random.choice(characters) for i in range(length))

    try:
        keycloak_admin = KeycloakAdmin(
            server_url=config["keycloak"]["server_url"],
            realm_name=config["keycloak"]["realm_name"],
            client_id=config["keycloak"]["client_id"],
            client_secret_key=config["keycloak"]["client_secret"],
            user_realm_name=config["keycloak"]["realm_name"],
            verify=True,
        )
    except KeycloakConnectionError:
        return email, False, None

    # Check if the user already exists
    user_id = keycloak_admin.get_user_id(email)
    if user_id:
        raise UserExistsException(
            "A user with this email address already exists. Contact the administrator if you need to recover your account."
        )

    # Calculate account expiration as Unix timestamp
    expiration_date = datetime.utcnow() + timedelta(days=expiration_days)

    # Format expiration timestamp as a human-readable string
    date_format = "%Y-%m-%d %H:%M:%S"
    formatted_expiration_date = expiration_date.strftime(date_format)

    # Create a new user
    user_data = {
        "username": email,
        "email": email,
        "enabled": True,
        "attributes": {
            "account_expiration_date": formatted_expiration_date,
        },
    }
    user_id = keycloak_admin.create_user(user_data)

    # Set a random temporary password
    temporary_password = generate_random_password()
    keycloak_admin.set_user_password(user_id, temporary_password, temporary=True)
    return keycloak_admin.get_user(user_id), temporary_password, expiration_date


# Function to assign a user to a group
def assign_user_to_group(user, group_name):
    try:
        keycloak_admin = KeycloakAdmin(
            server_url=config["keycloak"]["server_url"],
            realm_name=config["keycloak"]["realm_name"],
            client_id=config["keycloak"]["client_id"],
            client_secret_key=config["keycloak"]["client_secret"],
            user_realm_name=config["keycloak"]["realm_name"],
            verify=True,
        )
    except KeycloakConnectionError:
        return False

    # Get group
    try:
        group = keycloak_admin.get_group_by_path(group_name)
    except KeycloakGetError:
        return False  # Fail if Keycloak group throws exception finding group
    if not group:
        return False  # Also fail if Keycloak admin doesn't throw exception but group is still missing

    # Assign the user to the group
    keycloak_admin.group_user_add(user["id"], group["id"])

    return True


def get_theme():
    theme = config.get("theme", {})
    if theme:
        return {**DEFAULT_THEME, **theme}
    else:
        return DEFAULT_THEME


def get_template_context(request: Request, error_message: str = None):
    if (error_message is None) or (error_message == ""):
        return {
            "url_prefix": url_prefix,
            "request": request,
            "registration_message": config.get("registration_message", None),
            **get_theme(),
        }
    else:
        return {
            "url_prefix": url_prefix,
            "request": request,
            "registration_message": config.get("registration_message", None),
            "error_message": error_message,
            **get_theme(),
        }


@app.get(url_prefix)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", get_template_context(request))


@app.post(url_prefix + "/validate/")
async def validate_submission(request: Request, email: str = Form(...), coupon_code: str = Form(...)):
    if coupon_code in config.get("coupons", []):
        if check_email_domain(email):

            # Create the user in Keycloak
            try:
                user, temporary_password, expiration_date = create_keycloak_user(
                    email, config.get("account_expiration_days", None)
                )
            except UserExistsException as e:
                return templates.TemplateResponse("index.html", get_template_context(request, str(e)))

            # Assign user to group
            if user:
                success = assign_user_to_group(user, config.get("registration_group", None))

                if success:
                    return templates.TemplateResponse(
                        "success.html",
                        {
                            "url_prefix": url_prefix,
                            "request": request,
                            "email": email,
                            "temporary_password": temporary_password,
                            "user_id": user["id"],
                            "expiration_date": expiration_date.strftime("%m-%d-%Y"),
                            **get_theme(),
                        },
                    )
                else:
                    return templates.TemplateResponse(
                        "index.html",
                        get_template_context(
                            request,
                            "User created but could not be assigned to JupyterLab group.  Please contact support for assistance.",
                        ),
                    )
            else:
                return templates.TemplateResponse(
                    "index.html",
                    get_template_context(request, "Unable to create user.  Please try again later."),
                )

        else:
            return templates.TemplateResponse(
                "index.html",
                get_template_context(
                    request,
                    "Access to the platform is limited to accounts created with pre-approved email domains. The email address you provided when registering your account uses a domain that's not currently approved. Please contact the system administrator to request access.",
                ),
            )
    else:
        return templates.TemplateResponse(
            "index.html",
            get_template_context(request, "Invalid coupon code. Please try again."),
        )
