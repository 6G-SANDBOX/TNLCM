# Changelog

## [Unreleased]

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

## [v0.1.0] - 2023-09-29

### Added

- Basic Trial Network lifecycle management.
- Basic API.
- Basic Frontend.
- Initial data structures.

[unreleased]: https://github.com/6G-SANDBOX/TNLCM/compare/v0.1.0...HEAD
[v0.1.0]: https://github.com/6G-SANDBOX/TNLCM/releases/tag/v0.1.0