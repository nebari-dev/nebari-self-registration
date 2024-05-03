# Nebari Plugin Self Registration

[![PyPI - Version](https://img.shields.io/pypi/v/nebari-plugin-self-registration.svg)](https://pypi.org/project/nebari-plugin-self-registration)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/nebari-plugin-self-registration.svg)](https://pypi.org/project/nebari-plugin-self-registration)

-----

**Table of Contents**

- [Installation](#installation)
- [License](#license)

## Installation

```console
pip install nebari-plugin-self-registration
```

## User Registration via this extension
Steps for self registration:

- Navigate to your Nebari domain.
<p align="center">
  <img src="images/main-landing.png" />
</p>

- Click the link at "To register for an account, click here." or go to https://{your-domain-name}/registration

<p align="center">
  <img src="images/account-register.png" />
</p>

- Enter your email address and coupon code.

- After clicking "Submit" follow the instructions to login with your temporary password. By clicking the "Login" button, it will take you to a Welcome page where you can sign in with Keycloak.

<p align="center">
  <img src="images/account-register.png" />
</p>

- After you have entered a new password, you will receive a verification email.  

<p align="center">
  <img src="images/account-confirm.png" />
</p>

- Once your email is verified and you login you should see the Nebari landing page.

<p align="center">
  <img src="images/nebari-landing.png" />
</p>

## License

`nebari-plugin-self-registration` is distributed under the terms of the [Apache](./LICENSE.md) license.
