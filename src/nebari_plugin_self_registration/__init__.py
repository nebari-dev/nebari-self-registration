import inspect
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from _nebari.stages.base import NebariTerraformStage
from _nebari.stages.tf_objects import NebariKubernetesProvider, NebariTerraformState
from nebari.hookspecs import NebariStage, hookimpl
from nebari.schema import Base

NUM_ATTEMPTS = 10
TIMEOUT = 10

CLIENT_NAME = "self-registration"


class SelfRegistrationAffinitySelectorConfig(Base):
    default: str
    app: Optional[str] = ""
    job: Optional[str] = ""

class SelfRegistrationAffinityConfig(Base):
    enabled: Optional[bool] = True
    selector: Union[SelfRegistrationAffinitySelectorConfig, str] = "general"


class SelfRegistrationConfig(Base):
    name: Optional[str] = "self-registration"
    namespace: Optional[str] = None
    values: Optional[Dict[str, Any]] = {}
    account_expiration_days: Optional[int] = 7
    approved_domains: Optional[List[str]] = []
    coupons: Optional[List[str]] = []
    registration_group: Optional[str] = ""
    registration_message: Optional[str] = ""
    affinity: SelfRegistrationAffinityConfig = SelfRegistrationAffinityConfig()


class InputSchema(Base):
    self_registration: SelfRegistrationConfig = SelfRegistrationConfig()


class SelfRegistrationStage(NebariTerraformStage):
    name = "self-registration"
    priority = 103
    wait = True  # wait for install to complete on nebari deploy
    input_schema = InputSchema

    def tf_objects(self) -> List[Dict]:
        return [
            NebariTerraformState(self.name, self.config),
            NebariKubernetesProvider(self.config),
        ]

    @property
    def template_directory(self):
        return Path(inspect.getfile(self.__class__)).parent / "terraform"

    def _attempt_keycloak_connection(
        self,
        keycloak_url,
        username,
        password,
        master_realm_name,
        client_id,
        client_realm_name,
        verify=False,
        num_attempts=NUM_ATTEMPTS,
        timeout=TIMEOUT,
    ):
        from keycloak import KeycloakAdmin
        from keycloak.exceptions import KeycloakError

        for i in range(num_attempts):
            try:
                realm_admin = KeycloakAdmin(
                    keycloak_url,
                    username=username,
                    password=password,
                    user_realm_name=master_realm_name,
                    realm_name=client_realm_name,
                    client_id=client_id,
                    verify=verify,
                )
                c = realm_admin.get_client_id(CLIENT_NAME)  # lookup client guid
                existing_client = realm_admin.get_client(c)  # query client info
                if existing_client != None and existing_client["name"] == CLIENT_NAME:
                    print(f"Attempt {i+1} succeeded connecting to keycloak and nebari client={CLIENT_NAME} exists")
                    return True
                else:
                    print(
                        f"Attempt {i+1} succeeded connecting to keycloak but nebari client={CLIENT_NAME} did not exist"
                    )
            except KeycloakError as e:
                print(f"Attempt {i+1} failed connecting to keycloak {client_realm_name} realm -- {e}")
            time.sleep(timeout)
        return False

    def check(self, stage_outputs: Dict[str, Dict[str, Any]], disable_prompt=False) -> bool:

        try:
            _ = self.config.escaped_project_name
            _ = self.config.provider

        except KeyError:
            print("\nBase config values not found: escaped_project_name, provider")
            return False

        keycloak_config = self.get_keycloak_config(stage_outputs)

        if not self._attempt_keycloak_connection(
            keycloak_url=keycloak_config["keycloak_url"],
            username=keycloak_config["username"],
            password=keycloak_config["password"],
            master_realm_name=keycloak_config["master_realm_id"],
            client_id=keycloak_config["master_client_id"],
            client_realm_name=keycloak_config["realm_id"],
            verify=False,
        ):
            print(
                f"ERROR: unable to connect to keycloak master realm and ensure that nebari client={CLIENT_NAME} exists"
            )
            sys.exit(1)

        print(f"Keycloak successfully configured with {CLIENT_NAME} client")
        return True

    def input_vars(self, stage_outputs: Dict[str, Dict[str, Any]]):
        keycloak_config = self.get_keycloak_config(stage_outputs)

        try:
            domain = stage_outputs["stages/04-kubernetes-ingress"]["domain"]

        except KeyError:
            raise Exception("Prerequisite stage output(s) not found: stages/04-kubernetes-ingress")

        chart_ns = self.config.self_registration.namespace
        create_ns = True
        if chart_ns == None or chart_ns == "" or chart_ns == self.config.namespace:
            chart_ns = self.config.namespace
            create_ns = False

        return {
            "chart_name": self.config.self_registration.name,
            "account_expiration_days": self.config.self_registration.account_expiration_days,
            "approved_domains": self.config.self_registration.approved_domains,
            "coupons": self.config.self_registration.coupons,
            "registration_group": self.config.self_registration.registration_group,
            "registration_message": self.config.self_registration.registration_message,
            "project_name": self.config.escaped_project_name,
            "realm_id": keycloak_config["realm_id"],
            "client_id": CLIENT_NAME,
            "base_url": f"https://{keycloak_config['domain']}/self-registration",
            "external_url": keycloak_config["keycloak_url"],
            "create_namespace": create_ns,
            "namespace": chart_ns,
            "ingress_host": domain,
            "overrides": self.config.self_registration.values,
            "affinity": {
                "enabled": self.config.self_registration.affinity.enabled,
                "selector": (
                    self.config.self_registration.affinity.selector.__dict__
                    if isinstance(
                        self.config.self_registration.affinity.selector, SelfRegistrationAffinitySelectorConfig
                    )
                    else self.config.self_registration.affinity.selector
                ),
            },
            "cloud_provider": self.config.provider,
            "theme": self.config.theme.jupyterhub.dict(),
        }

    def get_keycloak_config(self, stage_outputs: Dict[str, Dict[str, Any]]):
        directory = "stages/05-kubernetes-keycloak"

        return {
            "domain": stage_outputs["stages/04-kubernetes-ingress"]["domain"],
            "keycloak_url": f"{stage_outputs[directory]['keycloak_credentials']['value']['url']}/auth/",
            "username": stage_outputs[directory]["keycloak_credentials"]["value"]["username"],
            "password": stage_outputs[directory]["keycloak_credentials"]["value"]["password"],
            "master_realm_id": stage_outputs[directory]["keycloak_credentials"]["value"]["realm"],
            "master_client_id": stage_outputs[directory]["keycloak_credentials"]["value"]["client_id"],
            "realm_id": stage_outputs["stages/06-kubernetes-keycloak-configuration"]["realm_id"]["value"],
        }


@hookimpl
def nebari_stage() -> List[NebariStage]:
    return [SelfRegistrationStage]
