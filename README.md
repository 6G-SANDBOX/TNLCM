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
2. Create a [Python virtual environment](https://virtualenv.pypa.io/en/stable/). All components can share the same
virtual environment.

`python -m venv <virtualenv name>`

3. Activate the virtual environment.
4. Install the requirements in the virtual environment.

`pip install -r requirements.txt`

### Starting `/core`

1. Activate the virtual environment.
2. Navigate to the `/core` folder
3. Run `python app.py`. `/core` will start listening for connections on port 5000.

### Starting `/frontend`

1. Activate the virtual environment.
2. Navigate to the `/frontend` folder
3. Run `python app.py`. `/frontend` will start listening for connections on port 5001.

## Settings

Setting files for all components are stored in the `/SETTINGS` folder. Example files indicating the expected format
and default configuration values are available in the `/SETTINGS/samples` folder. If the required settings file do
not exist when starting a component, the component will automatically create a configuration file using the default
values.

> It is not advisable to delete or otherwise edit the files in `/SETTINGS/samples`. 

### Configuration files

The following configuration files exist. More information about the format and values of each file can be seen in
their corresponding `.sample` file.

#### - `components.yml`

Used by `\core`. Contains the definition of all component types available in the platform, including references to
the 6G-Library repository that contains their playbook, which are defined in `repositories.yml`.

#### - `core.yml`

Used by `\core`. Contains basic functionality settings for the `\core` component.

#### - `repositories.yml`

Used by `\core`. Contains the definition of all available 6G-Library repositories. Repositories defined in this
file are referenced in `components.yml`.

## Trial Network Descriptor

> The format of Trial Network Descriptors has not been finalized and is expected to change in the future.

Trial Network Descriptors are yaml files with a set of expected fields and structure. This repository contains two
examples of descriptors, both describing the same Trial Network:
- `sample_descriptor.yml` describes the network as an additional component inside the infrastructure.
- `sample_descriptor_2.yml` uses separate sections for networks and infrastructure.

It is expected that the second example will be more representative of the final Trial Network Descriptor format,
however, the current implementation expects the format on `sample_descriptor.yml`, which the following section
will describe.

### Trial Network Descriptor schema:

```yaml
Infrastructure:  # Mandatory, contains the description of all entities in the Trial Network
  <Entity1>:  # A unique identifier for each entity in the Trial Network
    Type:  # Mandatory, reference to the corresponding component type in the 6G-Library
    Model:  # Optional, reference to a specific physical device or subtype of component
    Expose:  # Optional, list runtime values that should be provided to experimenters, such as ids, credentials or interfaces for accessing the entity
    Parameters:  # Optional, dictionary of values that further customize the entity. The available values are specified as part of the component's entry in the 6G-Library
      <Parameter1>: <Value1>
      # ...
    Connections:  # Optional, for each connection that the entity may have (as specified in the 6G-Library), to which <component>.<interface> it should be connected.
      <Connection1>: <EntityN>.<Interface1>
      # ...
    Monitor:  # Optional, for probes, list of entities to monitor
      - EntityN
    Store:  # Optional, list of values to keep after deletion of the Trial Network

```

## Authors

* **[Bruno Garcia Garcia](https://github.com/NaniteBased)**