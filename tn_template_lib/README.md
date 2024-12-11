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

## [open5gs_oneKE](./open5gs_oneKE.yaml)

![open5gs_oneKE](./images/open5gs_oneKE.png)

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

## [upf_p4_sw](./upf_p4_sw.yaml)

![upf_p4_sw](./images/upf_p4_sw.png)

### Components

* tn_init
* vnet
* upf_p4_sw
* ueransim (gnb and ue separated)
* vm_kvm

### Platforms

* uma
* athens
* berlin
* oulu

## [int_p4_sw](./int_p4_sw.yaml)

![int_p4_sw](./images/int_p4_sw.png)

### Components

* tn_init
* vnet
* int_p4_sw
* vm_kvm

### Platforms

* uma
* athens
* berlin
* oulu

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

## [open5gs_vm_ueransim_both](./open5gs_vm_ueransim_both.yaml)

![open5gs_vm_ueransim_both](./images/open5gs_vm_ueransim_both.png)

### Components

* tn_init
* vnet
* open5gs_vm
* ueransim (all in one)

### Platforms

* berlin
* uma
* athens
* oulu