from datetime import datetime, timedelta
from fastapi import FastAPI, Form, Request
from fastapi.templating import Jinja2Templates
import string
import random
import yaml
from keycloak import KeycloakAdmin, KeycloakConnectionError, KeycloakGetError
import os

print(os.getcwd())

app = FastAPI()
templates = Jinja2Templates(directory="templates")

file_path = "/mnt/config.yaml"
with open(file_path, "r") as file:
    config = yaml.safe_load(file)

def check_email_domain(email):
    approved_domains = config.get("approved_domains", [])
    for domain in approved_domains:
        if email.endswith(f"@{domain}"):
            return True
    return False

def create_keycloak_user(email, expiration_days=7):
    # Random password generator
    def generate_random_password(length=12):
        characters = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choice(characters) for i in range(length))

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
        return email, False


    # Check if the user already exists
    user_id = keycloak_admin.get_user_id(email)
    if user_id:
        return user_id, True

    # Calculate account expiration as Unix timestamp
    expiration_date = datetime.utcnow() + timedelta(days=expiration_days)

    # Format expiration timestamp as a human-readable string
    date_format="%Y-%m-%d %H:%M:%S"
    formatted_expiration_date = expiration_date.strftime(date_format)

    # Create a new user
    user_data = {
        "username": email,
        "email": email,
        "enabled": True,
        "attributes": {
            "approved": "true",
            "account_expiration_date": formatted_expiration_date,
        },
    }
    user_id = keycloak_admin.create_user(user_data)

    # Set a random temporary password
    temporary_password = generate_random_password()
    keycloak_admin.set_user_password(user_id, temporary_password, temporary=True)
    return keycloak_admin.get_user(user_id), temporary_password

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
        return False # Fail if Keycloak group throws exception finding group
    if not group:
        return False  # Also fail if Keycloak admin doesn't throw exception but group is still missing

    # Assign the user to the group
    keycloak_admin.group_user_add(user["id"], group["id"])
    
    return True

@app.get("/registration/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/registration/validate/")
async def validate_submission(request: Request, email: str = Form(...), coupon_code: str = Form(...)):
    if coupon_code in config.get("coupons", []):
        if check_email_domain(email):
            
            # Create the user in Keycloak
            user, temporary_password = create_keycloak_user(email, config.get("account_expiration_days", None))

            # Assign user to group
            if user:
                success = assign_user_to_group(user, config.get("registration_group", None))

                if success:
                    return templates.TemplateResponse("success.html", {"request": request, "email": email, "temporary_password": temporary_password, "user_id": user["id"]})
                else:
                    return templates.TemplateResponse("index.html", {"request": request, "error_message": "Your user was registered but could not be granted access to JupyterLab environments.  Please contact support for assistance."})
            else:
                return templates.TemplateResponse("index.html", {"request": request, "error_message": "Unable to create user.  Please try again later."})

        else:
            return templates.TemplateResponse("index.html", {"request": request, "error_message": "Email address is not allowed. Please use a different email address."})
    else:
        return templates.TemplateResponse("index.html", {"request": request, "error_message": "Invalid coupon code. Please try again."})