
ssh into the servers, use ubuntu user (change IPs)
```bash
ssh ubuntu@100.25.136.155 -i /Users/dborncamp/.ssh/moriarity2-2020
```

Update repos and install docker & kubernetes

```bash
sudo apt update
sudo apt install -y docker.io
sudo systemctl start docker
sudo systemctl enable docker


sudo usermod -aG docker $USER

curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add
sudo apt-add-repository "deb http://apt.kubernetes.io/ kubernetes-xenial main"
sudo apt-get install kubeadm kubelet kubectl -y


```

## Networking
At this point the servers should have everything installed so next we need to work on networking.
The easiest way (with some security) to allow the necessary communication between the nodes is to go into the AWS console and change the security groups to allow for needed ingress ports.
(Info on the ports can be found here)[https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/install-kubeadm/].
Set the security group to allow for inbound TCP connections for ports:
- 6443
- 2379-2380
- 10250-10252
- 30000-32767
Set source to custom and select the security group it is already using (ex `launch-wizard-3`).
Strictly speaking, only the master node needs 6443, but it is easiest to apply the same security group to all of the nodes

## back to servers
Edit the `/etc/hosts` for convenience, add the private IPs (changing for IP's):

```
172.31.21.9 kubemaster
172.31.24.231 kubenode1
172.31.31.195 kubenode2
```

# ONLY On Master
On master start the admin worker.
make sure to change cidr for addresses

```bash
sudo kubeadm init --pod-network-cidr=172.31.0.0/16
```

Now copy the config

```bash
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```


Must deploy a pod network now.
Use flannel, it is popular and seems to work?

```bash
kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml
```


Get the join command with tokens:

```bash
kubeadm token create --print-join-command
```


# On Nodes

Use the join command to join the master kubernetes node, must be run as sudo on the worker nodes, should be something like:
```bash
sudo kubeadm join 172.31.61.95:6443 --token jlm1eh.1paev2s0fenvg6wt     --discovery-token-ca-cert-hash sha256:26aa3eae4f7310b2e8ffd2b100652041c22b0131152f178b56dd22e9b8bf667f
```


# Testing
At this point it *should* be up and working, an easy way to tell is run `kubectl get nodes` it should show the master node and the worker nodes.

```
ubuntu@ip-172-31-61-95:~$ kubectl get nodes
NAME               STATUS   ROLES    AGE   VERSION
ip-172-31-53-2     Ready    <none>   19s   v1.18.6
ip-172-31-56-152   Ready    <none>   82s   v1.18.6
ip-172-31-61-95    Ready    master   17s   v1.18.6
```


## Install Helm

It is easiest to install using snap

```bash
sudo snap install helm --classic
```



#SNAGS

- Cannot connect to the kubernetes cluster locally even if I make a security group that allows for EVERYTHING
- After using Flannel I cannot egress from the EC2 instance

