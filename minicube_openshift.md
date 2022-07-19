# Installation

https://docs.okd.io/latest/minishift/getting-started/setting-up-virtualization-environment.html

Start with the environment and dependencies:

``` bash
brew install docker-machine-driver-xhyve
sudo chown root:wheel $(brew --prefix)/opt/docker-machine-driver-xhyve/bin/docker-machine-driver-xhyve
sudo chmod u+s $(brew --prefix)/opt/docker-machine-driver-xhyve/bin/docker-machine-driver-xhyve

brew install hyperkit
brew install docker-machine-driver-hyperkit
sudo chown root:wheel /usr/local/opt/docker-machine-driver-hyperkit/bin/docker-machine-driver-hyperkit
sudo chmod u+s /usr/local/opt/docker-machine-driver-hyperkit/bin/docker-machine-driver-hyperkit

brew install openshift-cli
```

Install minishift:

``` bash
brew cask install minishift
```

## Start it

Now we can actually start minishift:

``` bash
minishift start
```

A lot of things will be printed out and will download an openshift image.

Use minishift oc-env to display the command you need to type into your shell in order to add the oc binary to your PATH environment variable.

``` bash
minishift oc-env
```

May need to update the image registry.
Then build the images again.

```bash
eval $(minishift docker-env)
```

Start the openshift cluster.
Make sure that kubernetties is not running as part of docker desktop or this will take out the port it needs.
You may also need to add `"insecure-registries": ["172.30.0.0/16"]` to the docker engine config.
May not be needed anymore

```bash
oc config use-context minishift
oc cluster up --skip-registry-check=true --loglevel=2
```

Login to the openshift cluster as admin or developer.
To get the token, login to the console, click the question mark at the top amd go to command line tools.

default credentials are
• Username:developer
• Password:developer

``` bash
oc login -u system:admin
# or copied login from the console
oc login https://127.0.0.1:8443 --token=V-dHICFeI1-U6VDjBtCSt3FqjArpC6sx_wEkl-51Eqs
```

Create a new project.
By default, newer versions of OS will create one called `myproject`

``` bash
oc new-project myproject --display-name 'My Project'
```

Create a spacy app:

Deploy the image into the resository:

```bash
docker login -u developer -p $(oc whoami -t) $(minishift openshift registry)
docker push $(minishift openshift registry)/myproject/my-app
```

```bash
oc new-app --insecure-registry=true --docker-image=spacy:test --name=spacy-test
```

Update the image with a fresh image:

```bash
oc rollout latest "spacy-test"
```

Expose a route to the service:

``` bash
oc expose dc/spacy --port=9000
```

To determine the URL for the OpenShift cluster, for use when logging in from the command line or accessing the web console from a browser, run the command

``` bash
minishift console --url
```

## Stopping

Take down all openshift containers:

```bash
oc delete all --all
```

Stop minishift keeping everything the same:

```bash
minishift stop
```

Delete everything in minishift

``` bash
minishift delete
```

## Random/Usefull

``` bash
kubectl create secret generic docker.secret --from-file=.dockerconfigjson=/home/ubuntu/.docker/config.json --type=kubernetes.io/dockerconfigjson


oc whoami --show-server

```

## With Helm 2

Make sure to login first

```bash
oc login -u system:admin
```

### Get tiller set up

Create a new tiller project in openshift

```bash
oc new-project tiller
```

if one already exists use:

```bash
oc project tiller
```

Now export that namespace name to make things easier later

```bash
export TILLER_NAMESPACE=tiller
```

Start up the tiller server within the Openshift Mesh

```bash
oc process -f https://github.com/openshift/origin/raw/master/examples/helm/tiller-template.yaml -p TILLER_NAMESPACE="${TILLER_NAMESPACE}" -p HELM_VERSION=v2.16.7 | oc create -f -
```

Wait for the server to come up.
Check to make sure it is done

```bash
oc rollout status deployment tiller
```

## Helm project

Start a new project within Open Shift that will

```bash
oc new-project helm-test --display-name 'Helm Test'
```

Grant tiller edit access to the project

```bash
oc policy add-role-to-user edit "system:serviceaccount:${TILLER_NAMESPACE}:tiller"
```

Initialize helm/tiller

```bash
helm init
```

The version of helm needs to match the server, so use helmenv to get the exact correct version.
https://github.com/yuya-takeyama/helmenv

Install a pod

```bash
cd acm-server-3
helm install --name acm-server-3 --debug ./ --tiller-namespace cogintel
```

Delete a pod.
Must delete then install to redeploy

```bash
helm del --purge acm-server-3 --tiller-namespace cogintel
```

### May not be needed

Add a tiller namespace and service account

```bash
kubectl create serviceaccount --namespace kube-system tiller
kubectl create clusterrolebinding tiller-cluster-rule --clusterrole=cluster-admin --serviceaccount=kube-system:tiller
kubectl patch deploy --namespace kube-system tiller-deploy -p '{"spec":{"template":{"spec":{"serviceAccount":"tiller"}}}}'
```

Get all pods running everywhere

```bash
oc get pods --all-namespaces -o wide
```
