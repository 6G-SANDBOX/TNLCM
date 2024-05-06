# Changelog

## [Unreleased]

### Added

- Python version to 3.12.3.
- API using Python and the Flask-RESTX library.
- Different descriptors defining different trial networks.
- Detailed documentation including different sections about TNLCM.
- Routes for callback, sixglibrary, trial networks, users and verification.
- MongoDB database to manage the TNs.
- Flask-mongoengine as Mongo ORM.
- Docker compose to create MongoDB database.
- Integration with [6G-Library](https://github.com/6G-SANDBOX/6G-Library).
- Connection with Jenkins for the deployment of different components. Currently 8 types of components are running: tn_vxlan, tn_bastion, vm_kvm, vxlan, k8s, open5gs, UERANSIM-gNB and UERANSIM-UE.
- Logs to check TNLCM behavior.
- First integration with tests.

### Changed

- Create TNLCM from scratch.

### Removed

- Frontend implementation.

[unreleased]: https://github.com/6G-SANDBOX/TNLCM