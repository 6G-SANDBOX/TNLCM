<a name="readme-top"></a>

# TRIAL NETWORKS

> [!IMPORTANT]
> **MORE DESCRIPTORS IN THE [6G-LIBRARY](https://github.com/6G-SANDBOX/6G-Library) COMPONENTS DIRECTORIES. THE NAME OF THE DESCRIPTOR FILE FOLLOWS THE STRUCTURE `sample_tnlcm_descriptor.yaml`**.
> 
> [**EXAMPLE**](https://github.com/6G-SANDBOX/6G-Library/blob/main/elcm/sample_tnlcm_descriptor.yaml)

## [loadcore_open5gs_k8s](loadcore_open5gs_k8s.yaml)

![loadcore_open5gs_k8s](https://github.com/6G-SANDBOX/6G-Library/blob/assets/loadcore/loadcore_open5gs_k8s.png)

### Components

* tn_init
* vnet
* oneKE
* open5gs_k8s
* loadcore_agent

### Platforms

* uma
* athens
* berlin
* oulu

## [loadcore_open5gs_vm](loadcore_open5gs_vm.yaml)

![loadcore_open5gs_vm](https://github.com/6G-SANDBOX/6G-Library/blob/assets/loadcore/loadcore_open5gs_vm.png)

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

## [nokia_radio](./nokia_radio.yaml)

![nokia_radio](https://github.com/6G-SANDBOX/6G-Library/blob/assets/nokia_radio/nokia_radio.png)

### Components

* tn_init
* vnet
* oneKE
* open5gs_k8s
* nokia_radio
* stf_ue

### Platforms

* uma

## [ueransim_split_open5gs_k8s](./ueransim_split_open5gs_k8s.yaml)

![ueransim_split_open5gs_k8s](https://github.com/6G-SANDBOX/6G-Library/blob/assets/ueransim/ueransim_split_open5gs_k8s.png)

### Components

* tn_init
* vnet
* oneKE
* open5gs_k8s
* ueransim (gnb and ue separated)

### Platforms

* uma
* athens
* berlin
* oulu

## [ueransim_both_open5gs_k8s](./ueransim_both_open5gs_k8s.yaml)

![ueransim_both_open5gs_k8s](https://github.com/6G-SANDBOX/6G-Library/blob/assets/ueransim/ueransim_both_open5gs_k8s.png)

### Components

* tn_init
* vnet
* oneKE
* open5gs_k8s
* ueransim (all in one)

### Platforms

* uma
* athens
* berlin
* oulu

<p align="right"><a href="#readme-top">Back to top&#x1F53C;</a></p>
