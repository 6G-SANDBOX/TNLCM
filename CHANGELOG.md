# Changelog

## [Unreleased] - XXXX-XX-XX

### Added

- Hoppscotch directory, which contains a JSON file with collections of requests for the TNLCM API.
- Namespace for handler 6G-Sandbox-Sites repository requests.
- New endpoints to integrate TNLCM backend with frontend.
- New variables `SITES_BRANCH` and `JENKINS_TNLCM_DIRECTORY` in `.env` file to set the branch of the 6G-Sandbox-Sites repository.
- In the callback route accept requests only from Jenkins.

### Changed

- Rename script `installer.sh` to `install.sh`.
- Rename script `updater.sh` to `upgrade.sh`.
- Rename endpoints using `/api/v1/` prefix.
- Upgrade script with new steps.
- Document `.env.template` file with new variables.
- Move `cli` to `utils`.

### Fixed

- Bug when clone 6G-Library and 6G-Sandbox-Sites.
- Callback route integrate json body to handle the data received by Jenkins.

### Removed

- Mail configuration created for registration and password recovery.
- Collection `verification_token` from Mongo database.
- Model `VerificationToken` from `models` directory.
- Directory `callback` from `core` directory.

## [v0.4.5] - 2025-02-06

### Added

- Namespace for handler library requests.
- Script to update TNLCM version. It will start working from version 0.4.5 onwards.

### Changed

- Migrate from pyyaml library to ruamel.yaml library to handle YAML files.
- Migrate package manager from poetry to uv.
- Rename script `deploy_vm.sh` to `installer.sh`.
- Trial network descriptor validator.
- Change 6G-Sandbox-Sites option to use branch only.

### Fixed

- Two logs are recorded, one for each trial network and one for the generic TNLCM.

### Removed

- Directory: temporary.
- Check when a component of the output received by Jenkins is deployed with the one specified in the library.
- Docker installation.
- Some basic descriptors and added to 6G-Library.

## [v0.4.4] - 2024-12-04

### Added

- File `CONTRIBUTING.md` in `tn_template_lib` directory to explain the steps for how to add new descriptors.
- Possibility of skip two factor authentication.
- Endpoint that enable download report file of trial network in mardown format.
- `FLASK_ENV` variable in `.env` file to set the environment of the application.
- If `FLASK_ENV=development` can specify the repository url of 6G-Library and 6G-Sandbox-Sites when create a trial network.

### Changed

- Increase sleep time to verify if the component is deployed in Jenkins.
- Rename descriptors names in the `tn_template_lib` folder.
- If `FLASK_ENV=development` Swagger UI show `debug` namespace.

### Fixed

- Validate trial network descriptor in evaluate boolean expression.
- Different flows according to the possible states that can occur when purge a trial network.
- Script `deploy_vm.sh` to install TNLCM and MongoDB in a virtual machine.

## [v0.4.3] - 2024-11-15

### Changed

- Flask library to latest version 3.1.0.
- Migrated from `requirements.txt` to `pyproject.toml` for dependency management.
- Documentation updated with priority information and the rest of the documentation added on the [wiki](https://github.com/6G-SANDBOX/TNLCM/wiki).

## [v0.4.2] - 2024-11-08

### Added

- Create `input` and `output` directories per each trial networks.
- New field in `trial_network` collection called `input` that contains the inputs files sent to Jenkins.
- New field in `trial_network` collection called `output` that contains the json received by Jenkins.
- New directory `callback_handler` for control the data received by Jenkins.
- Image of trial networks templates.

### Changed

- Rename collection `verification_tokens` to `verification_token` in MongoDB.

### Fixed

- If an error occurs during TN creation, the created directory is now deleted to prevent inconsistencies.
- When purge trial network, also remove pipelines in Jenkins used for deploy and destroy trial network.
- Validate trial network descriptor when one of the components forming the trial network is tn_init, add tn_vxlan and tn_bastion.

### Removed

- Collection `callback` from Mongo database.

## [v0.4.1] - 2024-10-30

### Fixed

- Generalization of the functions defined in the file `file_handler.py` in the `utils` directory.
- Purge trial network when state is **validated**.
- Email validation updated to skip MX record check for `MAIL_USERNAME`. Now allows sending emails from domains without an MX record by setting `check_deliverability=False` in the `validate_email` function.
- Remove `users` collection create by default. The correct name of collection is `user`.

## [v0.4.0] - 2024-10-24

### Added

- **Concurrency** support in the Flask application by integrating **Gunicorn** to handle multiple simultaneous requests, improving responsiveness and performance.
- **Trial network isolation** to run several networks in parallel. The number of parallel trial networks is determined by the value of the environment variable `GUNICORN_WORKERS` minus 1. By default, `GUNICORN_WORKERS` is set to 3, allowing two trial networks to be executed concurrently. To execute sequentially, the number of `GUNICORN_WORKERS` has to be 2.
- **TNLCM folder is created in jenkins.** For each trial network its own pipeline is created to guarantee the isolation and to be able to execute several at the same time.
- **TRIAL_NETWORKS readme file** added in the `docs` directory to explain defined trial networks.
- **Initial CLI handler** to execute commands.
- **Git switch method** for streamlined repository management.
- **Callback collection** in database for answers generated by jenkins on entity deployment.
- **Utils directory** with required functions.
- **Scripts directory** with the following deployment scripts:
  - `deploy_vm.sh`: deploy TNLCM and MongoDB in a virtual machine.
  - `deploy_docker.sh`: deploy TNLCM and MongoDB using Docker.

### Changed

- Updated Python to version **3.13.0**.
- Updated MongoDB to version **8.0**.
- **Improved README documentation** for better clarity and usage guidelines.
- Migrated from the `ansible-vault` library to `ansible-core` since only this module is of interest.
- Renamed `ANSIBLE_VAULT` variable in `.env.template` to `SITES_TOKEN` for clarity.
- Moved the implementation from the `resource_manager` directory to the resource manager within the `models` directory.
- Rename `trial_networks`, `users` and `verification_tokens` collections to `trial_network`, `user` and `verification_token`.
- Rename columns `tn_state`, `tn_date_created_utc`, `tn_raw_descriptor`, `tn_sorted_descriptor`, `tn_deployed_descriptor`, `tn_report` and `tn_directory_path` to `state`, `date_created_utc`, `raw_descriptor`, `sorted_descriptor`, `deployed_descriptor`, `report` and `directory_path` in `trial_network` collection.

### Fixed

- Resolved a bug when creating a trial network, where components were defined in the 6G-Sandbox-Sites repository but not in the 6G-Library.
- Trial network can be destroyed if it is in **failed** state.
- Corrected function documentation to reflect accurate information.
- Message display when checking if a user can access a trial network.
- Enhanced logging for TNLCM processes.
- Issues with JWT and MongoDB error handling.
- Simplified class exception handling for improved readability and maintainability.
- Descriptors are converted from being stored in json to dictionaries in the `trial_networks` collection of the database.

### Removed

- **Deprecated API namespaces**:
  - Trial network templates.
  - 6G-Library.
  - 6G-Sandbox-Sites.

## [v0.3.1] - 2024-10-04

### Added

- Creation of an administrator user when instantiating the mongo database for the first time.

### Fixed

- Types of input values in the test descriptors of the `tn_template_lib` folder.
- Check if the site entered to deploy a trial network is correct.

## [v0.3.0] - 2024-09-25

### Added

- Debug namespace for developers.
  - Endpoints for modify the commits of the 6G-Sandbox-Sites and 6G-Library repositories associated to a trial network.
  - Endpoints for add or delete debug in specific entity_name.
  - Endpoint for check pipelines available in Jenkins.

### Changed

- Python version to 3.12.6.
- MongoDB version to 7.0.14.
- Libraries to latest versions.
- Update the extension of the docker compose file to .yaml.
- Rename `descriptors` folder to `tn_template_lib`.
- Added parameter for the TN_DESTROY pipeline with the list of components that need an additional script to be removed.
- Rename .env variables for pipeline deploy name and pipeline destroy name.

### Fixed

- Condition required when in 6G-Library.

### Removed

- Jenkins namespace of Swagger UI.

## [v0.2.1] - 2024-07-22

### Changed

- Docker version to 27.0.3.

### Fixed

- Launch a trial network when there are no builds of the pipeline yet in Jenkins.
- Destroy a trial network when there are no builds of the pipeline yet in Jenkins.

## [v0.2.0] - 2024-07-18

### Added

- Resource Manager to control the availability of resources per platform​.
- Descriptor validation.
- Initial version of state machine. Available methods:
  - validated
  - activated
  - failed
  - destroyed
- Integration with 6G-Sandbox-Sites repository.
- Ansible vault to decrypt files of site stored in 6G-Sandbox-Sites repository.
- Integration with 6G-Library [v0.2.0](https://github.com/6G-SANDBOX/6G-Library/releases/tag/v0.2.0).
- Deploy trial networks using specific branch, commit or tags from 6G-Library.
- Deploy trial networks using specific pipelines.
- Destroy trial networks using specific pipelines.
- Indicate the site where the trial network will be deployed. Connection to the site is required.
- Only components that are available on the indicated site can be deployed.
- [`11 descriptor files`](./tn_template_lib/) that each platform must pass or not pass as a test.

### Changed

- TNLCM is **only** available on Linux.
- Python version to 3.12.4.
- MongoDB version to 7.0.12.
- Trial network descriptor schema. Two new fields name and type. Also debug can included for Jenkins pipeline (optional).
- Mongoengine as Mongo ORM.
- Logs to check TNLCM behavior.
- Rename folder `src` to `core`.
- Libraries to latest versions.
- Repository documentation.
- Endpoints that define the API.

### Fixed

- Mongo volumes in docker compose file.

### Removed

- First integration with pytest.

## [v0.1.0] - 2024-05-16

### Added

- Different descriptors defining different trial networks.
- Detailed documentation including different sections about TNLCM.
- API using Python and the [Flask-RESTX](https://flask-restx.readthedocs.io/en/latest/) library.
- Routes for callback, sixglibrary, trial networks, users and verification.
- Docker compose for MongoDB database to manage the TNs.
- Integration with 6G-Library [v0.1.0](https://github.com/6G-SANDBOX/6G-Library/releases/tag/v0.1.0).
- Connection with Jenkins for the deployment of different components. Currently 8 types of components are running: 
  - tn_vxlan
  - tn_bastion
  - vm_kvm
  - vxlan
  - k8s_medium
  - open5gs
  - UERANSIM-gNB
  - UERANSIM-UE
- Logs to check TNLCM behavior.
- First integration with pytest.

### Changed

- Create TNLCM from scratch.

### Removed

- Frontend implementation.

[Unreleased]: https://github.com/6G-SANDBOX/TNLCM/compare/v0.4.5...HEAD
[v0.4.5]: https://github.com/6G-SANDBOX/TNLCM/compare/v0.4.4...v0.4.5
[v0.4.4]: https://github.com/6G-SANDBOX/TNLCM/compare/v0.4.3...v0.4.4
[v0.4.3]: https://github.com/6G-SANDBOX/TNLCM/compare/v0.4.2...v0.4.3
[v0.4.2]: https://github.com/6G-SANDBOX/TNLCM/compare/v0.4.1...v0.4.2
[v0.4.1]: https://github.com/6G-SANDBOX/TNLCM/compare/v0.4.0...v0.4.1
[v0.4.0]: https://github.com/6G-SANDBOX/TNLCM/compare/v0.3.1...v0.4.0
[v0.3.1]: https://github.com/6G-SANDBOX/TNLCM/compare/v0.3.0...v0.3.1
[v0.3.0]: https://github.com/6G-SANDBOX/TNLCM/compare/v0.2.1...v0.3.0
[v0.2.1]: https://github.com/6G-SANDBOX/TNLCM/compare/v0.2.0...v0.2.1
[v0.2.0]: https://github.com/6G-SANDBOX/TNLCM/compare/v0.1.0...v0.2.0
[v0.1.0]: https://github.com/6G-SANDBOX/TNLCM/releases/tag/v0.1.0