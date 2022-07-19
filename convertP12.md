# To extract pem files from a p12 use:


## Certificate

```bash
openssl pkcs12 -in <cert>.p12 -out <new_cert>.crt -clcerts -nokeys
```


## Key

```bash
openssl pkcs12 -in <cert>.p12 -out <new_cert>.key -nocerts -nodes
```

## CA

```bash
openssl pkcs12 -in <cert>.p12 -cacerts -nokeys -chain -out <new_cert>-ca.pem

```


## Get the DN out

```bash
openssl x509 -in <cert> -noout -subject -nameopt RFC2253
```
