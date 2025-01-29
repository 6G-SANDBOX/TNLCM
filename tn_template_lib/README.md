# TRIAL NETWORKS

> [!IMPORTANT]
> **MORE DESCRIPTORS IN THE 6G-LIBRARY COMPONENTS DIRECTORIES. THE NAME OF THE DESCRIPTOR FILE IS `sample_tnlcm_descriptor.yaml.yaml`**

## [ueransim_split](./ueransim_split.yaml)

![ueransim_split](./images/ueransim_split.png)

### Components

* tn_init
* vnet
* oneKE
* open5gs
* ueransim (gnb and ue separated)

### Platforms

* uma
* athens
* berlin
* oulu

## [ueransim_both](./ueransim_both.yaml)

![ueransim_both](./images/ueransim_both.png)

### Components

* tn_init
* vnet
* oneKE
* open5gs
* ueransim (all in one)

### Platforms

* uma
* athens
* berlin
* oulu

## [nokia_radio](./nokia_radio.yaml)

![nokia_radio](./images/nokia_radio.png)

### Components

* tn_init
* vnet
* oneKE
* open5gs
* nokia_radio
* stf_ue

### Platforms

* uma

## [loadcore_open5gs_oneKE](loadcore_open5gs_oneKE.yaml)

![loadcore_open5gs_oneKE](./images/loadcore_open5gs_oneKE.png)

### Components

* tn_init
* vnet
* oneKE
* open5gs
* loadcore_agent

### Platforms

* uma
* athens
* berlin
* oulu

## [loadcore_open5gs_vm](loadcore_open5gs_vm.yaml)

![loadcore_open5gs_vm](./images/loadcore_open5gs_vm.png)

### Components

* tn_init
* vnet
* open5gs_vm
* loadcore_agent

### Platforms

* berlin
* uma
* athens
* oulu