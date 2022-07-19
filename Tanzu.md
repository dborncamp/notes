# Tanzu

Tanzu Administrator account: `u: administrator@vsphere.local p: Health11Check!!`

Login:

```bash
~/downloads/vsphere-plugin/bin/kubectl-vsphere login --server 10.72.32.12 --insecure-skip-tls-verify -u administrator@vsphere.local --tanzu-kubernetes-cluster-name gitlab-runner-cl
```

To play with the gitlab runner, use the gitlab runner context:

```bash
kubectl config use-context gitlab-runner-ns
```
