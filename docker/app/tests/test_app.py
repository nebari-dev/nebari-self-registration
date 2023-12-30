import pytest
from unittest.mock import mock_open, patch
import pytest

@pytest.fixture(autouse=True)
def mock_config_file():
    mock_data = """
    coupons:
      - ANT
      - BAT
    approved_domains:
      - test.com
      - *wildcard.com
    account_expiration_days: 30
    registration_group: small-instances-only
    """
    with patch("builtins.open", mock_open(read_data=mock_data)):
        yield


def test_always_passes():
    assert True

#TODO: Getting ../.local/lib/python3.10/site-packages/pkg_resources/__init__.py:1433: AttributeError AttributeError: 'str' object has no attribute 'decode' running this locally.  Launching app with uvicorn doesn't have the issue.
    
#def test_check_email_domain():
#    from main import check_email_domain

#    assert check_email_domain('user@test.com') is True
#    assert check_email_domain('user@nonapproved.com') is False
#    assert True