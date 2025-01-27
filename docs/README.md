<a name="readme-top"></a>

<div align="center">

  # TRIAL NETWORK LIFECYCLE MANAGER <!-- omit in toc -->

  [![Contributors][contributors-shield]][contributors-url]
  [![Forks][forks-shield]][forks-url]
  [![Stargazers][stars-shield]][stars-url]
  [![Issues][issues-shield]][issues-url]
  <!-- [![MIT License][license-shield]][license-url] -->
  <!-- [![LinkedIn][linkedin-shield]][linkedin-url] -->

  <a href="https://github.com/6G-SANDBOX/TNLCM"><img src="./images/logo.png" width="100" title="TNLCM"></a>

  [![TNLCM][tnlcm-badge]][tnlcm-url]

  [Report error](https://github.com/6G-SANDBOX/TNLCM/issues/new?assignees=&labels=&projects=&template=bug_report.md) · [Feature request](https://github.com/6G-SANDBOX/TNLCM/issues/new?assignees=&labels=&projects=&template=feature_request.md) · [Wiki](https://github.com/6G-SANDBOX/TNLCM/wiki)
</div>

TNLCM (Trial Network Lifecycle Manager) is a tool designed to manage the lifecycle of trial networks in research and development environments, including integration with advanced technologies such as 6G. It provides features for creating, deploying, monitoring, and deleting experimental networks, ensuring efficient resource management. Additionally, it includes an API, a clear MongoDB database schema and support for defining networks through customizable descriptors.

<details>
<summary>Table of Contents</summary>

- [:round\_pushpin: Roadmap](#round_pushpin-roadmap)
- [:rocket: Getting Started Locally](#rocket-getting-started-locally)
  - [:inbox\_tray: Download the installation script](#inbox_tray-download-the-installation-script)
  - [:desktop\_computer: Execute installation script](#desktop_computer-execute-installation-script)
  - [:snake: Start server](#snake-start-server)
- [:hammer\_and\_wrench: Stack](#hammer_and_wrench-stack)
- [:books: Documentation](#books-documentation)
</details>

## :round_pushpin: Roadmap

- :white_check_mark: enhance validate trial network descriptor.
- :white_check_mark: update logs.
- Modify state machine to update trial network.
- Add token for interaction between jenkins and tnlcm at callback endpoint.
- Integration with Slurm.

## :rocket: Getting Started Locally

> [!IMPORTANT]
> TNLCM requires the **prior** installation of:
> 
> | Repository       | Release                                                                                |
> | ---------------- | -------------------------------------------------------------------------------------- |
> | OpenNebula       | [v6.10](https://github.com/OpenNebula/one/releases/tag/release-6.10.0)                 |
> | MinIO            | [2024-07-04](https://github.com/minio/minio/releases/tag/RELEASE.2024-07-04T14-25-45Z) |
> | Jenkins          | [v2.462.3](https://github.com/jenkinsci/jenkins/releases/tag/jenkins-2.462.3)          |

> [!TIP]
> Additionally TNLCM depends on:
>
> | Repository       | Release                                                                | Branch                                                     |
> | ---------------- | ---------------------------------------------------------------------- | ---------------------------------------------------------- |
> | 6G-Library       | [v0.3.1](https://github.com/6G-SANDBOX/6G-Library/tree/release/v0.3.1) | -                                                          |
> | 6G-Sandbox-Sites | -                                                                      | [platform](https://github.com/6G-SANDBOX/6G-Sandbox-Sites) |

### :inbox_tray: Download the installation script

Download the installation script which is [`installer.sh`](../scripts/installer.sh) and is located in the `scripts` directory.

### :desktop_computer: Execute installation script

Give execution permissions to the script:

```bash
chmod +x installer.sh
```

Run the script and follow the instructions:

```bash
source installer.sh
```

### :snake: Start server

```bash
gunicorn -c conf/gunicorn_conf.py
```

A Swagger UI will be available at the url http://tnlcm-backend-ip:5000 where the API with the endpoints exposed.

## :hammer_and_wrench: Stack
- [![Python][python-badge]][python-url] - Programming language.
- [![Flask][flask-badge]][flask-url] - Python framework for web applications to expose the API.
- [![MongoDB][mongodb-badge]][mongodb-url] - NoSQL database designed to store Trial Networks.

## :books: Documentation

Find the complete documentation and usage guides in our [docs](https://6g-sandbox.github.io/docs/docs/category/tnlcm).

## Contributors <!-- omit in toc -->

<a href="https://github.com/6G-SANDBOX/TNLCM/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=6G-SANDBOX/TNLCM" />
</a>

<p align="right"><a href="#readme-top">Back to top&#x1F53C;</a></p>

<!-- Urls, Shields and Badges -->
[tnlcm-badge]: https://img.shields.io/badge/TNLCM-v0.4.4-blue
[tnlcm-url]: https://github.com/6G-SANDBOX/TNLCM/releases/tag/v0.4.4
[python-badge]: https://img.shields.io/badge/Python-3.13.1-blue?style=for-the-badge&logo=python&logoColor=white&labelColor=3776AB
[python-url]: https://www.python.org/downloads/release/python-3131/
[flask-badge]: https://img.shields.io/badge/Flask-3.1.0-brightgreen?style=for-the-badge&logo=flask&logoColor=white&labelColor=000000
[flask-url]: https://flask.palletsprojects.com/en/stable/
[mongodb-badge]: https://img.shields.io/badge/MongoDB-8.0-green?style=for-the-badge&logo=mongodb&logoColor=white&labelColor=47A248
[mongodb-url]: https://www.mongodb.com/
[contributors-shield]: https://img.shields.io/github/contributors/6G-SANDBOX/TNLCM.svg?style=for-the-badge
[contributors-url]: https://github.com/6G-SANDBOX/TNLCM/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/6G-SANDBOX/TNLCM.svg?style=for-the-badge
[forks-url]: https://github.com/6G-SANDBOX/TNLCM/network/members
[stars-shield]: https://img.shields.io/github/stars/6G-SANDBOX/TNLCM.svg?style=for-the-badge
[stars-url]: https://github.com/6G-SANDBOX/TNLCM/stargazers
[issues-shield]: https://img.shields.io/github/issues/6G-SANDBOX/TNLCM.svg?style=for-the-badge
[issues-url]: https://github.com/6G-SANDBOX/TNLCM/issues
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://
[license-shield]: https://
[license-url]: https://