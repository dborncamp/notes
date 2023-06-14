# k3s Installation in vBPN

dborncamp's install notes for installing k3s on v-acmhp01-lx in the vBPN.
This keeps selinux at its default setting.

## Pre-Reqs

We will need the install repo, images, k3s binary, and SELinux Policy RPM.

- [Install Repo](https://gitlab.aero.ball.com/klaver/k3s/-/archive/master/k3s-master.zip): From https://gitlab.aero.ball.com/klaver/k3s
- [Images](https://github.com/k3s-io/k3s/releases/download/v1.26.3%2Bk3s1/k3s-airgap-images-amd64.tar.gz): From: https://github.com/k3s-io/k3s/releases/tag/v1.26.3%2Bk3s1
- [Binary](https://github.com/k3s-io/k3s/releases/download/v1.26.3%2Bk3s1/k3s): From https://github.com/k3s-io/k3s/releases/tag/v1.26.3%2Bk3s1
- [SELinux Policy RPM](https://github.com/k3s-io/k3s-selinux/releases/download/v1.2.stable.2/k3s-selinux-1.2-2.el8.noarch.rpm): From: https://github.com/k3s-io/k3s-selinux/releases

## Install Images

There are two ways to do the images, upload them to the local repo (Path One) or keep the tar in a special location and let k3s unpack them (Path Two).
I ended up going with Path Two.

### Path One

Unpack the tar and get the images in a good spot.
Also move the tar for a full off line deployment.

```bash
podman tag localhost/rancher/mirrored-library-busybox:1.34.1 bsf.cpnidm.local/chimera/rancher/mirrored-library-busybox:1.34.1
podman tag localhost/rancher/mirrored-metrics-server:v0.6.2 bsf.cpnidm.local/chimera/rancher/mirrored-metrics-server:v0.6.2
podman tag localhost/rancher/klipper-lb:v0.4.0 bsf.cpnidm.local/chimera/rancher/klipper-lb:v0.4.0
podman tag localhost/rancher/klipper-helm:v0.7.4-build20221121 bsf.cpnidm.local/chimera/rancher/klipper-helm:v0.7.4-build20221121
podman tag localhost/rancher/mirrored-library-traefik:2.9.4 bsf.cpnidm.local/chimera/rancher/mirrored-library-traefik:2.9.4
podman tag localhost/rancher/local-path-provisioner:v0.0.23 bsf.cpnidm.local/chimera/rancher/local-path-provisioner:v0.0.23
podman tag localhost/rancher/mirrored-coredns-coredns:1.9.4 bsf.cpnidm.local/chimera/rancher/mirrored-coredns-coredns:1.9.4
podman tag localhost/rancher/mirrored-pause:3.6 bsf.cpnidm.local/chimera/rancher/mirrored-pause:3.6

podman push bsf.cpnidm.local/chimera/rancher/mirrored-library-busybox:1.34.1
podman push bsf.cpnidm.local/chimera/rancher/mirrored-metrics-server:v0.6.2
podman push bsf.cpnidm.local/chimera/rancher/klipper-lb:v0.4.0
podman push bsf.cpnidm.local/chimera/rancher/klipper-helm:v0.7.4-build20221121
podman push bsf.cpnidm.local/chimera/rancher/mirrored-library-traefik:2.9.4
podman push bsf.cpnidm.local/chimera/rancher/local-path-provisioner:v0.0.23
podman push bsf.cpnidm.local/chimera/rancher/mirrored-coredns-coredns:1.9.4
podman push bsf.cpnidm.local/chimera/rancher/mirrored-pause:3.6

podman pull bsf.cpnidm.local/chimera/rancher/mirrored-library-busybox:1.34.1
podman pull bsf.cpnidm.local/chimera/rancher/mirrored-metrics-server:v0.6.2
podman pull bsf.cpnidm.local/chimera/rancher/klipper-lb:v0.4.0
podman pull bsf.cpnidm.local/chimera/rancher/klipper-helm:v0.7.4-build20221121
podman pull bsf.cpnidm.local/chimera/rancher/mirrored-library-traefik:2.9.4
podman pull bsf.cpnidm.local/chimera/rancher/local-path-provisioner:v0.0.23
podman pull bsf.cpnidm.local/chimera/rancher/mirrored-coredns-coredns:1.9.4
podman pull bsf.cpnidm.local/chimera/rancher/mirrored-pause:3.6
```

### Path Two

Copy the images to the correct location so that the offline scripts can find them.
Keep them `root:root`

```bash
sudo mkdir -p /var/lib/rancher/k3s/agent/images
sudo cp k3s-airgap-images-amd64.tar /var/lib/rancher/k3s/agent/images/
```

## Dependent Libraries

We don't want to disable selinux unless we have to, so install container-selinux, iptables, and selinux policy.
Install docker (actually podman to RHEL :( for good measure).

```bash
sudo dnf install -y container-selinux iptables docker
sudo dnf install -y k3s-selinux-1.2-2.el8.noarch.rpm --nogpgcheck
```

Copy the k3s executable to the $PATH

```bash
sudo cp k3s /usr/local/bin
chmod /usr/local/bin/k3s
```

## Start the Server

Unpack the repo and install

```bash
unzip k3s-master.zip
cd k3s-master/
INSTALL_K3S_SKIP_DOWNLOAD=true INSTALL_k3S_SKIP_SELINUX_RPM=true ./install.sh
```

## Interacting With the Server

Copy the config file

```bash
mkdir ${HOME}/.kube
cp /etc/rancher/k3s/k3s.yaml .kube/config
```

Configure pull secrets and deploy services.

```txt
kubectl create secret docker-registry vision-gitlab-registry --docker-username=group_10_bot --docker-password=<token> --docker-email=group_10_bot@cpn.local --docker-server=bsf.cpnidm.local
kubectl create secret docker-registry gitlab-registry --docker-username=group_68_bot1 --docker-password=<token> --docker-email=group_68_bot1@cpn.local --docker-server=bsf.cpnidm.local

helm repo add nexus.01 http://nexus.cpnidm.local/repository/chimera_helm/ --username v-dborncamp

helm install activemq nexus.01/activemq
helm install arm nexus.01/arm

v-dborncamp@CPN.local@v-amchp01-lx:~/k3s-master$ kubectl get pods -o wide
NAME                        READY   STATUS    RESTARTS      AGE   IP           NODE                        NOMINATED NODE   READINESS GATES
activemq-54d5f5cf64-k9pxs   1/1     Running   0             15h   10.42.0.11   v-amchp01-lx.cpnidm.local   <none>           <none>
arm-57cc5957b6-9dlj2        1/1     Running   0             15h   10.42.0.10   v-amchp01-lx.cpnidm.local   <none>           <none>
```
