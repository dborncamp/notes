# Tanzu CLI

Install the Tanzu CLI on Linux.

Note: for Gremlin on Aero the DSOA ticket that has the cluster information is [https://jira.aero.ball.com/browse/DSOA-2987](https://jira.aero.ball.com/browse/DSOA-2987)

## Pre Requesites

- tar
- gunzip
- install

Sudo access on the host.

## Download

Download the bundle package from the content repository  and move it onto the workstation.
It is in Nexus: raw_devapproved/tanzu/tanzu-cli-bundle-linux-amd64.tar.gz

## Installation

Create a new directory and unpack

```bash
export TANZU_DIR=<tanzu Directory> # /opt/tanzu
mkdir ${TANZU_DIR}
# Copy the downloaded bundle to the ${TANZU_DIR} directory
cp <Path/tanzu-cli-bundle-linux-amd64.tar.gz>  ${TANZU_DIR}
cd ${TANZU_DIR}
tar xvzf ${TANZU_DIR}/tanzu-cli-bundle-linux-amd64.tar.gz
```

This should create a `cli` directory.

Prepare the files for installation

```bash
cd ${TANZU_DIR}/cli
gunzip kapp-linux-amd64-v0.49.0+vmware.1.gz
gunzip imgpkg-linux-amd64-v0.29.0+vmware.1.gz
gunzip kbld-linux-amd64-v0.34.0+vmware.1.gz
gunzip vendir-linux-amd64-v0.27.0+vmware.1.gz
gunzip ytt-linux-amd64-v0.41.1+vmware.1.gz
tar xzf tanzu-framework-plugins-context-linux-amd64.tar.gz
tar xzf tanzu-framework-plugins-standalone-linux-amd64.tar.gz
```

Install the CLI

```bash
sudo install ${TANZU_DIR}/cli/core/v0.25.0/tanzu-core-linux_amd64 /usr/local/bin/tanzu
tanzu init  # (this initializes the Tanzu CLI)
```

Install the CLI plugins

```bash
tanzu plugin install login -l ${TANZU_DIR}/cli/standalone-plugins
tanzu plugin install package -l ${TANZU_DIR}/cli/standalone-plugins
tanzu plugin install pinniped-auth -l ${TANZU_DIR}/cli/standalone-plugins
tanzu plugin install secret -l ${TANZU_DIR}/cli/standalone-plugins
tanzu plugin install telemetry -l ${TANZU_DIR}/cli/standalone-plugins
```

Download and install `kubectl` from the content reposity and move it onto the workstation.
Note, there is nothing special about this relative to Tanzu, if you alreadu have kubectl, skip this step.

1. Get the binary from Nexus: raw_devapproved/tanzu/kubectl-linux-v1.23.8+vmware.2.gz
2. Copy the file to ${TANZU_DIR}
3. Unzip and install:

```bash
gunzip ${TANZU_DIR}/kubectl-linux-v1.23.8+vmware.2.gz
install ${TANZU_DIR}/kubectl-linux-v1.23.8+vmware.2 /usr/local/bin/kubectl
```

Install ytt

```bash
sudo cp ${TANZU_DIR}/cli/ytt-linux-amd64-v0.41.1+vmware.1 /usr/local/bin/ytt
# Not actually needed 
# chown root:root /usr/local/bin/ytt
sudo chmod 755 /usr/local/bin/ytt
ytt --version  # (To test)
```

Install kapp

```bash
sudo cp ${TANZU_DIR}/cli/kapp-linux-amd64-v0.49.0+vmware.1 /usr/local/bin/kapp
# Not actually needed 
# chown root:root /usr/local/bin/kapp
sudo chmod 755 /usr/local/bin/kapp
kapp --version  # (To test)
```

Install kbld

```bash
sudo cp ${TANZU_DIR}/cli/kbld-linux-amd64-v0.34.0+vmware.1 /usr/local/bin/kbld
# chown root:root /usr/local/bin/kbld
sudo chmod 755 /usr/local/bin/kbld
kbld --version  # (To test)
```

Install imgpkg

```bash
sudo cp ${TANZU_DIR}/cli/imgpkg-linux-amd64-v0.29.0+vmware.1 /usr/local/bin/imgpkg
# Not actually needed 
# chown root:root /usr/local/bin/imgpkg
sudo chmod 755 /usr/local/bin/imgpkg
imgpkg --version  # (To test)
```

## Configuring Login

Tanzu is generally not configured for an actual login, so we need to merge the `kubeconfig.yaml` in the DSOA ticket with existing `~/.kube/config` file.
To do this, copy the `cluster`, `context`, and `user` stanzas from the `kubeconfig.yaml` file into the approperate places in the `${HOME}/.kube/config` file.

After the configs are merged, attempt to access the cluster by switching to the tanzu context and do a get on the cluster.
Run:

```bash
kubectl config use-context tanzu-cli-dsoa-2987@dsoa-2987  # Note this context can change, use `kubectl config get-contexts` to see
kubectl get pods
```

It will give you a URL to log in with your LDAP Aero credentials.
Login to that URL and you can now use the cluster!
