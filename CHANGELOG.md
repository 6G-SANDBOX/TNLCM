# Changelog

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

[v0.3.1]: https://github.com/6G-SANDBOX/TNLCM/compare/v0.3.0...v0.3.1
[v0.3.0]: https://github.com/6G-SANDBOX/TNLCM/compare/v0.2.1...v0.3.0
[v0.2.1]: https://github.com/6G-SANDBOX/TNLCM/compare/v0.2.0...v0.2.1
[v0.2.0]: https://github.com/6G-SANDBOX/TNLCM/compare/v0.1.0...v0.2.0
[v0.1.0]: https://github.com/6G-SANDBOX/TNLCM/releases/tag/v0.1.0