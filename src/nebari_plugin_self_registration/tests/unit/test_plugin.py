import pytest
from nebari_plugin_self_registration import SelfRegistrationStage, SelfRegistrationConfig, InputSchema

class TestConfig(InputSchema):
    __test__ = False
    namespace: str
    domain: str
    escaped_project_name: str = ""
    provider: str = "local"
    self_registration: SelfRegistrationConfig = SelfRegistrationConfig(account_expiration_days = 14, approved_domains = ["test1.com","test2.org"], coupons = ["COUPON1","COUPON2"], registration_group = "test_group")

@pytest.fixture(autouse=True)
def mock_keycloak_connection(monkeypatch):
    monkeypatch.setattr("nebari_plugin_self_registration.SelfRegistrationStage._attempt_keycloak_connection", lambda *args, **kwargs: True)

def test_ctor():
    sut = SelfRegistrationStage(output_directory = None, config = None)
    assert sut.name == "self-registration"
    assert sut.priority == 103

def test_input_vars():
    config = TestConfig(namespace = "nebari-ns", domain = "my-test-domain.com", escaped_project_name="testprojectname")
    sut = SelfRegistrationStage(output_directory = None, config = config)


    stage_outputs = get_stage_outputs()
    sut.check(stage_outputs)
    result = sut.input_vars(stage_outputs)
    assert result["chart_name"] == "self-registration"
    assert result["account_expiration_days"] == 14
    assert result["approved_domains"] == ["test1.com","test2.org"]
    assert result["coupons"] == ["COUPON1","COUPON2"]
    assert result["registration_group"] == "test_group"
    assert result["project_name"] == "testprojectname"
    assert result["realm_id"] == "test-realm"
    assert result["client_id"] == "self-registration"
    assert result["base_url"] == "https://my-test-domain.com/self-registration"
    assert result["external_url"] == "https://my-test-domain.com/auth/"
    assert result["create_namespace"] == False
    assert result["namespace"] == "nebari-ns"
    assert result["ingress_host"] == "my-test-domain.com"
    assert result["overrides"] == {}

def test_default_namespace():
    config = TestConfig(namespace = "nebari-ns", domain = "my-test-domain.com", provider="aws")
    sut = SelfRegistrationStage(output_directory = None, config = config)

    stage_outputs = get_stage_outputs()
    result = sut.input_vars(stage_outputs)
    assert result["create_namespace"] == False
    assert result["namespace"] == "nebari-ns"

def test_chart_namespace():
    config = TestConfig(namespace = "nebari-ns", domain = "my-test-domain.com", provider="aws", self_registration = SelfRegistrationConfig(namespace = "self_registration-ns"))
    sut = SelfRegistrationStage(output_directory = None, config = config)

    stage_outputs = get_stage_outputs()
    result = sut.input_vars(stage_outputs)
    assert result["create_namespace"] == True
    assert result["namespace"] == "self_registration-ns"

def test_chart_overrides():
    config = TestConfig(namespace = "nebari-ns", domain = "my-test-domain.com", provider="aws", self_registration = SelfRegistrationConfig(values = { "foo": "bar" }))
    sut = SelfRegistrationStage(output_directory = None, config = config)

    stage_outputs = get_stage_outputs()
    result = sut.input_vars(stage_outputs)
    assert result["overrides"] == { "foo": "bar" }

def get_stage_outputs():
    return {
        "stages/02-infrastructure": {
            "cluster_oidc_issuer_url": {
                "value": "https://test-oidc-url.com"
            }
        },
        "stages/04-kubernetes-ingress": {
            "domain": "my-test-domain.com"
        },
        "stages/05-kubernetes-keycloak": {
            "keycloak_credentials": {
                "value": {
                    "url": "https://my-test-domain.com",
                    "username": "testuser",
                    "password": "testpassword",
                    "realm": "testmasterrealm",
                    "client_id": "testmasterclientid"
                }
            }
        },
        "stages/06-kubernetes-keycloak-configuration": {
            "realm_id": {
                "value": "test-realm"
            }
        }
    }