# Changelog

## [Unreleased]

### Added

- Integration with 6G-Sandbox-Sites repository.

### Changed

- Python version to 3.12.3.
- Descriptor schema.
- Mongoengine as Mongo ORM.
<!-- - API using Python and the FastAPI library. -->
- Logs to check TNLCM behavior.
- Rename folder src to core.
- Libraries to latest versions.
- Repository documentation.

## [v0.1.0] - 2024-05-16

### Added

- Different descriptors defining different trial networks.
- Detailed documentation including different sections about TNLCM.
- API using Python and the Flask-RESTX library.
- Routes for callback, sixglibrary, trial networks, users and verification.
- Docker compose for MongoDB database to manage the TNs.
- Integration with [6G-Library](https://github.com/6G-SANDBOX/6G-Library).
- Connection with Jenkins for the deployment of different components. Currently 8 types of components are running: tn_vxlan, tn_bastion, vm_kvm, vxlan, k8s, open5gs, UERANSIM-gNB and UERANSIM-UE.
- Logs to check TNLCM behavior.
- First integration with tests.

### Changed

- Create TNLCM from scratch.

### Removed

- Frontend implementation.

[unreleased]: https://github.com/6G-SANDBOX/TNLCM/compare/v0.1.0...HEAD
[v0.1.0]: https://github.com/6G-SANDBOX/TNLCM/releases/tag/v0.1.0