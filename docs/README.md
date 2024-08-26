<a name="readme-top"></a>

<div align="center">

  [![Contributors][contributors-shield]][contributors-url]
  [![Forks][forks-shield]][forks-url]
  [![Stargazers][stars-shield]][stars-url]
  [![Issues][issues-shield]][issues-url]
  <!-- [![MIT License][license-shield]][license-url] -->
  <!-- [![LinkedIn][linkedin-shield]][linkedin-url] -->

  <a href="https://github.com/6G-SANDBOX/TNLCM"><img src="./static/TNLCM.png" width="350" title="TNLCM"></a>

  [![TNLCM][tnlcm-badge]][tnlcm-url]

  [Report error](https://github.com/6G-SANDBOX/TNLCM/issues/new?assignees=&labels=&projects=&template=bug_report.md) · [Feature request](https://github.com/6G-SANDBOX/TNLCM/issues/new?assignees=&labels=&projects=&template=feature_request.md)
</div>

TNLCM has been designed as a modular application, with the intention of making certain components easily replaceable or extended, while minimizing the effect of changes in other parts of the application. At the same time, there is an emphasis on re-usability, where several data structures and generic logic can be shared between the different components of the application.

> [!NOTE]
> TNLCM is under development and is subject to continuous changes.

<details>
<summary>Table of Contents</summary>

- [:hammer\_and\_wrench: Stack](#hammer_and_wrench-stack)
- [:open\_file\_folder: Project Structure](#open_file_folder-project-structure)
- [:mag: Overview of TNLCM and 6G-Library implementation](#mag-overview-of-tnlcm-and-6g-library-implementation)
- [:arrows\_counterclockwise: State Machine](#arrows_counterclockwise-state-machine)
- [:hourglass\_flowing\_sand: Current Status](#hourglass_flowing_sand-current-status)
- [:rocket: Getting Started Locally](#rocket-getting-started-locally)
  - [:inbox\_tray: Download or clone repository](#inbox_tray-download-or-clone-repository)
  - [:wrench: Configure environment variables](#wrench-configure-environment-variables)
  - [:floppy\_disk: Create database](#floppy_disk-create-database)
  - [:snake: Create environment, install libraries and start](#snake-create-environment-install-libraries-and-start)
- [:page\_facing\_up: Trial Network Descriptor Schema](#page_facing_up-trial-network-descriptor-schema)
- [Appendices](#appendices)
  - [Appendix A: How to use Swagger UI](#appendix-a-how-to-use-swagger-ui)
  - [Appendix B: Database Schema](#appendix-b-database-schema)
  - [Appendix C: TNLCM OpenNebula Appliance](#appendix-c-tnlcm-opennebula-appliance)
</details>

## :hammer_and_wrench: Stack
- [![Python][python-badge]][python-url] - Programming language.
- [![Flask][flask-badge]][flask-url] - Python framework for web applications to expose the API.
- [![MongoDB][mongodb-badge]][mongodb-url] - NoSQL database designed to store Trial Networks.
- [![Docker][docker-badge]][docker-url] - Platform for running database applications.

## :open_file_folder: Project Structure

```
TNLCM/                       // main folder.
├─ .github/                  // folder contains files and templates for GitHub workflow automation.
│  ├─ CHANGELOG_TEMPLATE/    // folder with template for changelog.
│  └─ ISSUE_TEMPLATE/        // folder with template for issue reporting.
├─ .gitignore                // file specifying intentionally untracked files to ignore.
├─ app.py                    // main file that starts TNLCM.
├─ CHANGELOG.md              // file containing the changes made in each release.
├─ descriptors/              // folder in which trial network descriptors templates are stored.
├─ docker-compose.yaml       // file for create database.
├─ docs/                     // folder in which all documentation is stored.
├─ requirements.txt          // file containing the libraries and their versions.
├─ conf/                     // folder that handler the configuration files.
└─ core/                     // folder in which the developed code is stored.
   ├─ auth/                  // folder that handler the authentication of users who have access.
   ├─ callback/              // folder that handler the results received by Jenkins.
   ├─ database/              // folder that handler the connection with MongoDB database using mongoengine.
   ├─ exceptions/            // folder that handler the creation of custom exceptions.
   ├─ jenkins/               // folder that handler the connection with Jenkins for tn deployment.
   ├─ logs/                  // folder that handler the logs configuration.
   ├─ mail/                  // folder that handler the configuration to use flask mail library.
   ├─ models/                // folder that contains the database models.
   ├─ repository/            // folder that handler the connection to any repository.
   ├─ resource_manager/      // folder that handler the resource manager.
   ├─ routes/                // folder that handler the API that is exposed.
   ├─ sixg_library/          // folder that handler the connection to the 6G-Library repository.
   ├─ sixg_sandbox_sites/    // folder that handler the connection to the 6G-Sandbox-Sites repository.
   └─ temp/                  // folder that handler the creation of temporary files.
```

## :mag: Overview of TNLCM and 6G-Library implementation

![TNLCM_LIFECYCLE](./static/TNLCM_6GLIBRARY.png)

<p align="right"><a href="#readme-top">Back to top&#x1F53C;</a></p>

## :arrows_counterclockwise: State Machine

![StateMachine](./static/stateMachine.png)

<p align="right"><a href="#readme-top">Back to top&#x1F53C;</a></p>

## :hourglass_flowing_sand: Current Status

TNLCM is currently able to deploy the following types of components corresponding with the [6G-Library](https://github.com/6G-SANDBOX/6G-Library): **tn_vxlan**, **tn_bastion**, **tn_init**, **vnet**, **tsn**, **vm_kvm**, **oneKE**, **open5gs**, **UERANSIM-gNB** and **UERANSIM-UE**.

![CurrentStatus](./static/currentStatus.png)

<p align="right"><a href="#readme-top">Back to top&#x1F53C;</a></p>

## :rocket: Getting Started Locally

> [!NOTE]
> TNLCM is being developed and tested on Ubuntu in version 22.04.3 LTS.

> [!TIP]
> TNLCM uses the following repository releases:
> 
> | Repository       | Branch | Release                                                                      |
> | ---------------- | ------ | ---------------------------------------------------------------------------- |
> | 6G-Library       | -      | [v0.2.0](https://github.com/6G-SANDBOX/6G-Library/releases/tag/v0.2.0)       |
> | 6G-Sandbox-Sites | main   | -                                                                            |

> [!WARNING]
> In order to run TNLCM, the following tools are **required** to be deployed on the platforms:
>
> * OpenNebula: v6.6.3 or later
>
> From [OpenNebula Marketplace](https://marketplace.mobilesandbox.cloud:9443/appliance):
> 
> * Jenkins
> * MinIO
> * OneKE: v1.27 or v1.29
> * Ueransim: v3.2.6

### :inbox_tray: Download or clone repository

Download the **main** branch from the TNLCM repository.

Clone repository:

```sh
git clone https://github.com/6G-SANDBOX/TNLCM
```

### :wrench: Configure environment variables

Create a `.env` file at the root level, using the structure and content provided in the [`.env.template`](../.env.template) file.

Mandatory update the values of the following variables according to the platform:
- `TNLCM_HOST`
- `JENKINS_HOST`
- `JENKINS_USERNAME`
- `JENKINS_PASSWORD`
- `JENKINS_TOKEN`
- `ANSIBLE_VAULT`
<!-- - `MAIL_USERNAME`
- `MAIL_PASSWORD` -->

Optionally, the value of the following variables can be updated:
- `FLASK_ENV`
- `ME_CONFIG_BASICAUTH_USERNAME`
- `ME_CONFIG_BASICAUTH_PASSWORD`

### :floppy_disk: Create database

> [!IMPORTANT]
> This step requires **Docker** :whale: to be installed on the machine.

- [Linux](https://docs.docker.com/engine/install/ubuntu/)

Once Docker is installed, open a terminal where the [`docker-compose.yaml`](../docker-compose.yaml) file is stored (usually inside the TNLCM project) and execute the command:

```sh
docker compose up -d
```

Flag **-d** can be added to raise the containers in background.

A MongoDB dashboard will be available at the url http://mongodb-frontend-ip:8081 where the database can be managed.

> [!NOTE]
> User and password to access to the MongoDB dashboard are the values indicated in the variables `ME_CONFIG_BASICAUTH_USERNAME` and `ME_CONFIG_BASICAUTH_PASSWORD` of the `.env` file. By default, the values indicated in the [`.env.template`](../.env.template) file are used.

![dashboardMongoDB](./static/dashboardMongoDB.png)

### :snake: Create environment, install libraries and start

> [!IMPORTANT]
> This step requires **Python** to be installed on the machine.

The environment must be created inside the TNLCM folder:

- Linux

  ```sh
  # Create environment
  python3 -m venv venv

  # Activate environment
  source venv/bin/activate
  
  # Install libraries
  pip install -r requirements.txt
  ```

With the environment activated, start TNLCM:

```sh
python app.py
```

A Swagger UI will be available at the url http://tnlcm-backend-ip:5000 where the API with the endpoints can be seen.

<p align="right"><a href="#readme-top">Back to top&#x1F53C;</a></p>

## :page_facing_up: Trial Network Descriptor Schema
> [!WARNING]
> The format of Trial Network Descriptors has not been finalized and is expected to change in the future.

Trial Network Descriptors are yaml files with a set of expected fields and with the following structure:

```yaml
trial_network: # Mandatory, contains the description of all entities in the Trial Network
  type-name: # Mandatory, a unique identifier for each entity in the Trial Network (entity name)
    type: # Mandatory, 6G-Library component type
    name: # Mandatory, custom name. Not use character \- or \.
    debug: # Optional, param to debug component in Jenkins. Possible values true or false
    dependencies: # Mandatory, list of dependencies of the component with other components
      - type-name
      - ...
    input: # Mandatory, dictionary with the variables collected from the input part of the 6G-Library
      key: value
```

This repository contains a variety of descriptor templates:
- [`01_descriptor.yml`](../descriptors/01_descriptor.yml)
- [`02_descriptor.yml`](../descriptors/02_descriptor.yml)
- [`03_descriptor.yml`](../descriptors/03_descriptor.yml)
- [`04_descriptor.yml`](../descriptors/04_descriptor.yml)
- [`05_descriptor.yml`](../descriptors/05_descriptor.yml)
- [`06_descriptor.yml`](../descriptors/06_descriptor.yml)
- [`07_descriptor.yml`](../descriptors/07_descriptor.yml)
- [`08_descriptor.yml`](../descriptors/08_descriptor.yml)
- [`09_descriptor.yml`](../descriptors/09_descriptor.yml)
- [`10_descriptor.yml`](../descriptors/10_descriptor.yml)
- [`11_descriptor.yml`](../descriptors/11_descriptor.yml)

The first end-to-end trial network:
- [`08_descriptor.yml`](../descriptors/08_descriptor.yml)

<p align="right"><a href="#readme-top">Back to top&#x1F53C;</a></p>

## Appendices

### Appendix A: How to use Swagger UI

The API set forth in the TNLCM is as follows:

![api](./static/api.png)

If it is the first time using the API it is necessary to create a user. A verification code is required, so it is necessary to enter a valid email address that can be accessed:

![requestVerificationToken](./static/requestVerificationToken.png)

Once the registration code is obtained, proceed to the user registration using the email and the code previously employed:

![registerUser](./static/registerUser.png)

Once the user has been created or if it has been previously created, add the user and its password in the green **Authorize** box:

![addUser](./static/addUser.png)

Once the user has been added, an access token and its refresh token can be generated. This access token has a duration of 45 minutes (can be modified):

![tokens](./static/obtainTokens.png)

The next step is to add the token in the green **Authorize** box. It is required to put the word **Bearer**, a space and then the token. An example is shown:

![accessToken](./static/accessToken.png)

Now, requests that involve having an access token can be made.

To create a Trial Network, the following endpoint must be used:

![createTN](./static/createTN.png)

Once created, it will return a tn_id that will be required to deploy it.

To deploy a trial network, the following endpoint must be used:

![startTN](./static/startTN.png)

If the access token expires, it can be refreshed by using the refresh token. The token in the green **Authorize** box must be updated with the refresh token and the post request must be made:

![refreshToken](./static/refreshToken.png)

![updateAccessToken](./static/updateAccessToken.png)

When the request is made, it will return another access token that will need to be put back into the green **Authorize** box.

<p align="right"><a href="#readme-top">Back to top&#x1F53C;</a></p>

### Appendix B: Database Schema

The TNLCM database consists of several collections that store important information about trial networks, users, and verification tokens. Below is the description of each collection:

#### Collection `trial_networks` <!-- omit in toc -->

| Field                               | Description                                                                             |
| ----------------------------------- | --------------------------------------------------------------------------------------- |
| `user_created`                      | The user that created the trial network.                                                |
| `tn_id`                             | The ID of the trial network.                                                            |
| `tn_state`                          | The state of the trial network.                                                         |
| `tn_date_created_utc`               | The date and time when the trial network was created (UTC).                             |
| `tn_raw_descriptor`                 | The raw descriptor of the trial network.                                                |
| `tn_sorted_descriptor`              | The sorted descriptor of the trial network.                                             |
| `tn_deployed_descriptor`            | The current status of descriptor with the last entity deployed of the trial network.    |
| `tn_report`                         | The report related to the trial network.                                                |
| `deployment_job_name`               | The pipeline used for the deployment of the descriptor.                                 |
| `destroy_job_name`                  | The pipeline used for destroy a trial network.                                          |
| `deployment_site`                   | The site where the trial network has been deployed.                                     |
| `github_6g_library_commit_id`       | The commit id of 6G-Library (branch, commit or tag) used to deploy trial network.       |
| `github_6g_sandbox_sites_commit_id` | The commid id of 6G-Sandbox-Sites (branch, commit or tag) used to deploy trial network. |

#### Collection `trial_networks_templates` <!-- omit in toc -->

| Field                  | Description                                                          |
| ---------------------- | -------------------------------------------------------------------- |
| `user_created`         | The user that created the trial network template.                    |
| `tn_id`                | The ID of the trial network template.                                |
| `tn_date_created_utc`  | The date and time when the trial network template was created (UTC). |
| `tn_raw_descriptor`    | The raw descriptor of the trial network template.                    |
| `tn_sorted_descriptor` | The sorted descriptor of the trial network template.                 |

#### Collection `users` <!-- omit in toc -->

| Field      | Description                                 |
| ---------- | ------------------------------------------- |
| `email`    | The email address of the user.              |
| `username` | The username of the user.                   |
| `password` | The password of the user (hashed).          |
| `org`      | The organization to which the user belongs. |

#### Collection `verifications_tokens` <!-- omit in toc -->

| Field                | Description                                           |
| -------------------- | ----------------------------------------------------- |
| `new_account_email`  | The email associated with the new account.            |
| `verification_token` | The verification token generated for the new account. |
| `creation_date`      | The creation date of the verification token.          |

#### Collection `resource_manager` <!-- omit in toc -->

| Field       | Description                                                      |
| ----------- | ---------------------------------------------------------------- |
| `site`      | The site where the trial network has been deployed.              |
| `component` | The component over which the resources are controlled.           |
| `quantity`  | The amount of component available.                               |
| `ttl`       | The amount of time the component can be used in a trial network. |

<p align="right"><a href="#readme-top">Back to top&#x1F53C;</a></p>

### Appendix C: TNLCM OpenNebula Appliance

In the [marketplace-community](https://github.com/6G-SANDBOX/marketplace-community/wiki/tnlcm) repository, which is a fork of OpenNebula, detailed information about the TNLCM appliance can be found.

<p align="right"><a href="#readme-top">Back to top&#x1F53C;</a></p>

## :construction_worker: Development Team <!-- omit in toc -->

|                               Photo                                |        Name         |      Email      |                                                                        GitHub                                                                        |                                                                                      Linkedin                                                                                       |
| :----------------------------------------------------------------: | :-----------------: | :-------------: | :--------------------------------------------------------------------------------------------------------------------------------------------------: | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------: |
| <img src="https://github.com/CarlosAndreo.png?size=50" width=50px> | Carlos Andreo López | c.andreo@uma.es | <a href="https://github.com/CarlosAndreo"><img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white"></a> | <a href="https://www.linkedin.com/in/carlos-andreo-lópez-66734b22a/"><img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white"></a> |
| <img src="https://github.com/NaniteBased.png?size=50" width=50px>  | Bruno García García |        -        | <a href="https://github.com/NaniteBased"><img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white"></a>  |     <a href="https://itis.uma.es/personal/bruno-garcia-garcia/"><img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white"></a>      |

<p align="right"><a href="#readme-top">Back to top&#x1F53C;</a></p>

<!-- Urls, Shields and Badges -->
[tnlcm-badge]: https://img.shields.io/badge/TNLCM-v0.2.2-blue
[tnlcm-url]: https://github.com/6G-SANDBOX/TNLCM/releases/tag/v0.2.2
[python-badge]: https://img.shields.io/badge/Python-3.12.5-blue?style=for-the-badge&logo=python&logoColor=white&labelColor=3776AB
[python-url]: https://www.python.org/downloads/release/python-3124/
[flask-badge]: https://img.shields.io/badge/Flask-3.0.3-brightgreen?style=for-the-badge&logo=flask&logoColor=white&labelColor=000000
[flask-url]: https://flask.palletsprojects.com/en/3.0.x/
[mongodb-badge]: https://img.shields.io/badge/MongoDB-7.0.12-green?style=for-the-badge&logo=mongodb&logoColor=white&labelColor=47A248
[mongodb-url]: https://www.mongodb.com/
[docker-badge]: https://img.shields.io/badge/Docker-27.0.3-6AB7FF?style=for-the-badge&logo=docker&logoColor=white&labelColor=2496ED
[docker-url]: https://www.docker.com/
[contributors-shield]: https://img.shields.io/github/contributors/6G-SANDBOX/TNLCM.svg?style=for-the-badge
[contributors-url]: https://github.com/6G-SANDBOX/TNLCM/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/6G-SANDBOX/TNLCM.svg?style=for-the-badge
[forks-url]: https://github.com/6G-SANDBOX/TNLCM/network/members
[stars-shield]: https://img.shields.io/github/stars/6G-SANDBOX/TNLCM.svg?style=for-the-badge
[stars-url]: https://github.com/6G-SANDBOX/TNLCM/stargazers
[issues-shield]: https://img.shields.io/github/issues/6G-SANDBOX/TNLCM.svg?style=for-the-badge
[issues-url]: https://github.com/6G-SANDBOX/TNLCM/issues
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://www.linkedin.com/company/itisuma/
[license-shield]: https://
[license-url]: https://