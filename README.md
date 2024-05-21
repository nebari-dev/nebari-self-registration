# Nebari Plugin Self Registration

[![PyPI - Version](https://img.shields.io/pypi/v/nebari-plugin-self-registration.svg)](https://pypi.org/project/nebari-plugin-self-registration)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/nebari-plugin-self-registration.svg)](https://pypi.org/project/nebari-plugin-self-registration)

---

**Table of Contents**

- [Installation](#installation)
- [Configuration](#configuration)
- [License](#license)

## Installation
This project is meant to run as a plugin within a Nebari deployment. To learn how to get started with Nebari, check out the docs [here](https://www.nebari.dev/docs/welcome).

In order to install this plugin as part of a Nebari deployment:
- Create a conda environment for your Nebari deployment
- Install the self registration plugin with `pip install nebari-plugin-self-registration`
- Continue the initialization and deployment of Nebari per your provider [instructions](https://www.nebari.dev/docs/explanations/provider-configuration).

> **NOTE:** When running `nebari render` and `nebari deploy`, Nebari will detect and install any extensions which are installed in your Python environment.  When managing multiple Nebari deployments, be sure to manage your conda environments to ensure the correct extensions and versions are installed in your target deployment.


### Configuration
The configuration of your self registration app can be customized in several ways by creating a `config.yaml` file within the `self-registration` folder. An example of a configuration yaml is provided [here](https://github.com/MetroStar/nebari-self-registration/blob/main/self-registration/config.sample.yaml).

Configuration options include:


- **account_expiration_days (optional)**: Days a user is provided to verify their account.  Defaults to 7.
- **approved_domains (required)**: List of approved email domains that can register accounts using the self registration service.  (supports names like `gmail.com` and wildcards such as `*.edu`)
- **coupons (required)**: List of coupon codes that can be used by individuals during the self registration process.
- **registration_group (required)**: Keycloak group where all registering users will be added.  This group can then be used to assign user properties such as available JupyterLab instance types, app sharing permissions, etc.
- **name (optional)**: Name for resources that this extension will deploy via Terraform and Helm.  Defaults to `self-registration`
- **namespace (optional)**: Kubernetes namespace for this service.  Defaults to Nebari's default namespace.
- **registration_message (optional)**: A custom message to display on the landing page `/registration`
- **values (optional)**: Any additional values that will be passed to the Helm chart as `overrides`
- **affinity (optional)**: Set a custom Kubernetes affinity for the app and/or job.  Defaults to the `general` node group.


> **NOTE:** The `registration_group` must have been created in the Nebari realm in Keycloak prior to deploying the extension.

## Running locally with Docker

_Note_: running locally requires a `config.yaml` file to be present within the `self-registration` directory. Please create a copy of the `sample.config.yaml`, rename, and update as needed before proceeding:

1. Navigate to the `self-registration` directory
2. To build the docker image, run the following:

```
docker build . --file Dockerfile.local -t self-registration
```

3. To run the app, run the following:

```
docker run -p 8000:8000 --name self-registration self-registration
```

4. Navigate to http://0.0.0.0:8000/registration

## User Registration via this extension

Steps for self registration:

- Navigate to your Nebari domain.
<p align="center">
  <img src="images/welcome-nebari.png" />
</p>

- You may have a hyperlink on the welcome page that takes you to the user registration form. If not, navigate to https://{your-domain-name}/registration

<p align="center">
  <img src="images/account-register.png" width="400"/>
</p>

- Enter your email address and coupon code.

- After clicking "Submit" follow the instructions to login with your temporary password. By clicking the "Login" button, it will take you to a Welcome page where you can sign in with Keycloak.

- After you have entered a new password, you will receive a verification email.

<p align="center">
  <img src="images/account-confirm.png" />
</p>

- Once your email is verified and you login you will see the Nebari landing page.

<p align="center">
  <img src="images/nebari-splash.png" />
</p>

## License

`nebari-plugin-self-registration` is distributed under the terms of the [Apache](./LICENSE.md) license.
