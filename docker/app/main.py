from fastapi import FastAPI, Form, Request
from fastapi.templating import Jinja2Templates
import yaml
from keycloak import KeycloakAdmin, KeycloakConnectionError
import os

print(os.getcwd())

app = FastAPI()
templates = Jinja2Templates(directory="templates")
config = yaml.safe_load(open("config.yml"))

def check_email_domain(email):
    approved_domains = config.get("approved_domains", [])
    for domain in approved_domains:
        if email.endswith(f"@{domain}"):
            return True
    return False

def create_keycloak_user(email):

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

    # Create a new user
    user_data = {
        "username": email,
        "email": email,
        "enabled": True,
        "attributes": {"approved": "true"},
    }
    user_id = keycloak_admin.create_user(user_data)
    return user_id, True

@app.get("/registration/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/registration/validate/")
async def validate_coupon(request: Request, email: str = Form(...), coupon_code: str = Form(...)):
    if coupon_code in config.get("coupons", []):
        if check_email_domain(email):
            # Create the user in Keycloak
            user_id, success = create_keycloak_user(email)

            if success:
                return templates.TemplateResponse("success.html", {"request": request, "email": email, "coupon_code": coupon_code, "user_id": user_id})
            else:
                return templates.TemplateResponse("index.html", {"request": request, "error_message": "Unable to create user.  Please try again later."})

        else:
            return templates.TemplateResponse("index.html", {"request": request, "error_message": "Email address is not allowed. Please use a different email address."})
    else:
        return templates.TemplateResponse("index.html", {"request": request, "error_message": "Invalid coupon code. Please try again."})