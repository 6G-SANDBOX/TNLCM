**In progress** [Version 0.2.0]
- Added API using Python and the Flask-restx library
- Added MongoDB database to manage the deployed TNs
- Added connection to the 6G-Library
- Added connection with Jenkins for the deployment of different components. Currently 3 types of components are running: tn_vxlan, tn_bastion and vm_kvm
- Added logs to check TNLCM behavior
- Added detailed documentation with TNLCM deployment information as well as the descriptor schema
- Added authentication for user control via token. In this way, the linked Trial Networks can be identified for each user