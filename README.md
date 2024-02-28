[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python&logoColor=white&labelColor=3776AB)](https://www.python.org/downloads/release/python-3113/)
[![Flask](https://img.shields.io/badge/Flask-3.0.2+-brightgreen?style=for-the-badge&logo=flask&logoColor=white&labelColor=000000)](https://flask.palletsprojects.com/en/3.0.x/)

# Trial Network Life Cycle Manager

## Components

### Core `/core`

`/core` contains the basic functionality for managing the life-cycle of several Trial Networks in a single Testbed.
It also implements the TNLCM API. A description of the API is accessible via Swagger, when accessing to the root
endpoint

### Front-End `/frontend`

`/frontend` contains the initial implementation of a management dashboard for the TNLCM, which makes use of the
API provided by `/core` to operate.

### Shared `/shared`

`/shared` contains several classes that are useful for more than one component. These include the creation of log files,
access to CLI, or management of threads, among others.

`/shared/data` contains data structures, particularly the `TrialNetwork`, `Entity`, `TrialNetworkDescriptor`
and `EntityDescriptor`. These data structures encapsulate the usage of Trial Network Descriptors and the runtime
status of a Trial Network.

## Deployment

### Installation procedure

1. Ensure that Python 3.11 is installed in your system.
2. Create a [Python virtual environment](https://virtualenv.pypa.io/en/stable/). All components can share the same virtual environment.
* Windows:

  `python -m venv <virtualenv name>`

* Ubuntu:

  `python3 -m venv <virtualenv name>`

1. Activate the virtual environment.
* Windows:

  `./<virtualenv name>/Scripts/activate`

* Ubuntu:

  `source <virtualenv name>/bin/activate`

4. Install the requirements in the virtual environment.

`pip install -r requirements.txt`

### Settings

Setting files for all components are stored in the `/SETTINGS` folder. Example files indicating the expected format
and default configuration values are available in the `/SETTINGS/samples` folder. If the required settings file do
not exist when starting a component, the component will automatically create a configuration file using the default
values.

> It is not advisable to delete or otherwise edit the files in `/SETTINGS/samples`. 

#### Configuration files

The following configuration files exist. More information about the format and values of each file can be seen in
their corresponding `.sample` file.

##### - `components.yml`

Used by `\core`. Contains the definition of all component types available in the platform, including references to
the 6G-Library repository that contains their playbook, which are defined in `repositories.yml`.

```yaml
Components:
  tn_vxlan:
    Repository: 6gLibrary
    Branch: update_bastion
    # Commit: 9bd5ff96530015c6f3863527da1d97ea2ecb0391
    Folder: tn_vxlan
  tn_bastion:
    Repository: 6gLibrary
    Branch: update_bastion
    # Commit: 97c91f9c77765576ef0a6bb25f712e54fcfe216b
    Folder: tn_bastion
  vm_kvm_very_small:
    Repository: 6gLibrary
    Branch: update_bastion
    Folder: vm_kvm_very_small
```

##### - `core.yml`

Used by `\core`. Contains basic functionality settings for the `\core` component.

```yaml
Paths:
  Repositories: '../REPOSITORIES'
  TrialNetworks: '../TRIAL_NETWORKS'
```

##### - `repositories.yml`

Used by `\core`. Contains the definition of all available 6G-Library repositories. Repositories defined in this
file are referenced in `components.yml`.

```yaml
Repositories:
  6gLibrary:
    Address: "https://github.com/6G-SANDBOX/6G-Library"
    User:
    Password:
```

Also at the same level where the .env.template file is located, you must create the .env file that must contain the information of the .env.template file but filled in.

##### - `.env`

```.env
# Jenkins connection
JENKINS_SERVER=""
JENKINS_USER=""
JENKINS_PASSWORD=""
JENKINS_TOKEN=""
# Jenkins parameters
JENKINS_TN_ID=""
JENKINS_6GLIBRARY_BRANCH=""
JENKINS_DEPLOYMENT_SITE=""
# URL for Jenkins answers
CALLBACK_URL=""  # Need to deploy TNLCM on a virtual machine to which Jenkins has access
```

### Starting TNLCM

1. Activate the virtual environment.
2. Navigate to the `/core` folder.
3. Run `python app.py`. `/core` will start listening for connections on port 5000.
4. Enter Swagger UI: http://localhost:5000
5. You have to execute the POST request found in the TESTBED section to which you have to insert the descriptor file. In this repository there is a descriptor file available called: "first_descriptor.yml". This request will return an id which is needed for the next section.
6. Access the PUT endpoint in the trial_network section and indicate in the tnID field the id received in the previous step.

## Trial Network Descriptor

> The format of Trial Network Descriptors has not been finalized and is expected to change in the future.

Trial Network Descriptors are yaml files with a set of expected fields and structure. This repository contains an
example of descriptor:
- `first_descriptor.yml`

### Trial Network Descriptor schema:

```yaml
trial_network:  # Mandatory, contains the description of all entities in the Trial Network
  <Entity1>:  # A unique identifier for each entity in the Trial Network
    depends_on: # List of dependencies of the component with other components
      - <EntityN>
      - ...
    public: # Necessary variables collected from the public part of the 6G-Library
      ...
```