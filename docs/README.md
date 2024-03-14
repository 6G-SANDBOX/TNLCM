[![Python](https://img.shields.io/badge/Python-3.12+-blue?style=for-the-badge&logo=python&logoColor=white&labelColor=3776AB)](https://www.python.org/downloads/release/python-3122/)
[![Flask](https://img.shields.io/badge/Flask-3.0.2+-brightgreen?style=for-the-badge&logo=flask&logoColor=white&labelColor=000000)](https://flask.palletsprojects.com/en/3.0.x/)

# TRIAL NETWORK LIFECYCLE MANAGER (TNLCM)

## Deploy TNLCM

> ⚠ It is recommended to do this deployment on a virtual machine since you must use a callback URL that Jenkins must have access to.

### Download or clone repository

Download the main branch from the TNLCM repository

Clone repository:

        git clone https://github.com/CarlosAndreo/TNLCM.git

### Create .env using .env.template

> ⚠ The following tools are required to be deployed on the platforms:

* Jenkins (Mandatory)
* OpenNebula (Mandatory)
* MinIO (Optional)

Create the .env file at the same level and with the contents of the .env.template file.

### Create TNLCM database

> ⚠ This step requires Docker to be installed on the machine.

* [Windows](https://docs.docker.com/desktop/install/windows-install/)
* [Linux](https://docs.docker.com/desktop/install/linux-install/)

Once Docker is installed, open a terminal where the docker-compose.yml file is stored (usually inside the TNLCM project) and execute the commands:

        docker compose build

        docker compose up

### Create python environment and install libraries. 

The environment must be created inside the TNLCM project

* Windows

        # Create environment
        python -m venv venv

        # Activate environment
        ./venv/Scripts/activate.ps1

        # Install libraries
        pip install -r requirements.txt

* Linux

        # Create environment
        python3 -m venv venv

        # Activate environment
        source venv/bin/activate
        
        # Install libraries
        pip install -r requirements.txt

### Start TNLCM

With the environment activated, start TNLCM

    python app.py

## Trial Network Descriptor Schema

> The format of Trial Network Descriptors has not been finalized and is expected to change in the future.

Trial Network Descriptors are yaml files with a set of expected fields and structure. This repository contains an
example of descriptor:
- `first_descriptor.yml`

```yaml
trial_network:  # Mandatory, contains the description of all entities in the Trial Network
  <Entity1>:  # A unique identifier for each entity in the Trial Network
    depends_on: # List of dependencies of the component with other components
      - <EntityN>
      - ...
    public: # Necessary variables collected from the public part of the 6G-Library
      ...
```