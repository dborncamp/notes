# [Ingress](https://kubernetes.io/docs/concepts/services-networking/ingress/) and [Ingress Controllers](https://kubernetes.io/docs/concepts/services-networking/ingress-controllers/)

In modern k8s we must have an ingress controller to allow for ingress into a cluster.
This handles load balancing at the edge and different controllers can work different ways.
[Nginx ingress](https://github.com/kubernetes/ingress-nginx/) controller is one of the most common.
Their [docs page](https://kubernetes.github.io/ingress-nginx/) is pretty comprehensive.

## Single Ingress Controller

If there is only a single ingress controller for the cluster, set `.controller.ingressClassResource.default: true` in the nginx Helm chart.

The `.spec.ingressClassName` (formerly `kubernetes.io/ingress.class`) field of the Ingress object must match the ingress controller used.
Example IngressClass config:

```yaml
---
apiVersion: networking.k8s.io/v1
kind: IngressClass
metadata:
  labels:
    app.kubernetes.io/component: controller 
  name: nginx
  annotations:
    ingressclass.kubernetes.io/is-default-class: "true"
spec:
  controller: k8s.io/ingress-nginx
```

With the config above, add `spec.ingressClassName=nginx` as the `spec.ingressClassName` for the Ingress object.

One thing that got me was the hostname in the ingress.
If there is no url to connect it, it will likely fail to connect the ingress controller.
