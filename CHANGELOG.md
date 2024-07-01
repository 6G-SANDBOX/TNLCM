# Changelog

## [v0.2.1] - 2024-07-01

### Added

- Decrypt values.yaml file of site stored in 6G-Sandbox-Sites repository.

## [v0.2.0] - 2024-06-28

### Added

- Resource Manager to control the availability of resources per platform​.
- Descriptor validation.
- Initial version of state machine. Available methods:
  - validated
  - activated
  - failed
  - destroyed
- Integration with 6G-Sandbox-Sites repository.
- Integration with 6G-Library [v0.2.0](https://github.com/6G-SANDBOX/6G-Library/releases/tag/v0.2.0).
- Deploy trial networks using specific branch, commit or tags from 6G-Library.
- Deploy trial networks using specific pipelines/jobs.
- Destroy trial networks using specific pipelines/jobs.
- Indicate the site where the trial network will be deployed. Connection to the site is required.
- Only components that are available on the indicated site can be deployed.
- [`11 descriptor files`](./descriptors/) that each platform must pass or not pass as a test.

### Changed

- Python version to 3.12.4.
- MongoDB version to 7.0.11.
- Trial network descriptor schema. Two new fields name and type. Also debug can included for Jenkins pipeline (optional).
- Mongoengine as Mongo ORM.
- Logs to check TNLCM behavior.
- Rename folder `src` to `core`.
- Libraries to latest versions.
- Repository documentation.
- Endpoints that define the API.

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

[v0.2.1]: https://github.com/6G-SANDBOX/TNLCM/releases/tag/v0.2.1
[v0.2.0]: https://github.com/6G-SANDBOX/TNLCM/releases/tag/v0.2.0
[v0.1.0]: https://github.com/6G-SANDBOX/TNLCM/releases/tag/v0.1.0