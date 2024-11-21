# TRIAL NETWORKS

## [tn_vxlan](./tn_vxlan.yaml)

![tn_vxlan](./images/tn_vxlan.png)

### Components

* tn_vxlan

### Platforms

* uma
* athens
* berlin
* oulu

## [tn_bastion](./tn_bastion.yaml)

![tn_bastion](./images/tn_bastion.png)

### Components

* tn_vxlan
* tn_bastion

### Platforms

* uma
* athens
* berlin
* oulu

## [tn_init](./tn_init.yaml)

![tn_init](./images/tn_init.png)

### Components

* tn_init

### Platforms

* uma
* athens
* berlin
* oulu

## [vm_kvm](./vm_kvm.yaml)

![vm_kvm](./images/vm_kvm.png)

### Components

* tn_init
* vm_kvm

### Platforms

* uma
* athens
* berlin
* oulu

## [oneKE](./oneKE.yaml)

![oneKE](./images/oneKE.png)

### Components

* tn_init
* vnet
* oneKE

### Platforms

* uma
* athens
* berlin
* oulu

## [open5gs](./open5gs.yaml)

![open5gs](./images/open5gs.png)

### Components

* tn_init
* vnet
* oneKE
* open5gs

### Platforms

* uma
* athens
* berlin
* oulu

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

## [tsn](./tsn.yaml)

![tsn](./images/tsn.png)

### Components

* tn_init
* tsn

### Platforms

* uma

## [nokia](./nokia.yaml)

![nokia](./images/nokia.png)

### Components

* tn_init
* vnet
* oneKE
* open5gs
* nokia_radio
* stf_ue

### Platforms

* uma

## [ocf](./ocf.yaml)

![ocf](./images/ocf.png)

### Components

* tn_init
* vnet
* oneKE
* ocf (OpenCAPIF)

### Platforms

* uma
* athens
* berlin
* oulu

## [elcm](./elcm.yaml)

![elcm](./images/elcm.png)

### Components

* tn_init
* elcm

### Platforms

* uma
* athens
* berlin
* oulu

## [upf_p4](./upf_p4.yaml)

![upf_p4](./images/upf_p4.png)

### Components

* tn_init
* vnet
* upf_p4_sw
* ueransim (gnb and ue separated)
* vm_kvm

### Platforms

* uma

## [LOADCORE_WP5](loadcore_wp5.yaml)

![loadcore_wp5](./images/loadcore_wp5.png)

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