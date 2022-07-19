From Kyle in Slack (Decipher)

You can extract/create a bunch of other openssl certs you might need from this one p12!  For example...
The below openssl command will give you a text file that includes the contents of your your.name.crt (first block), your.name.chain.crt (first block + second block), and your.name.encryptedkey (third/last block)–just copy/paste these blocks into their own files.

```bash
openssl pkcs12 -in your.name.p12 -out more_certs.txt
```

If you need a your.name.key file, you will probably want to un-encrypt your.name.encryptedkey.  You can do this by...

```bash
openssl rsa -in your.name.encryptedkey -out your.name.key

openssl pkcs12 -in certs/quickstart.p12 -cacerts -nokeys -out observables/certs/ca.crt
openssl pkcs12 -in certs/quickstart.p12 -clcerts -nokeys -out observables/certs/user.crt
openssl pkcs12 -in certs/quickstart.p12 -nocerts -nodes -out observables/certs/user.key
```

Zoe uses this method to extract keys

```bash
openssl pkcs12 -in certs/quickstart.p12 -cacerts -nokeys -out observables/certs/ca.crt
openssl pkcs12 -in certs/quickstart.p12 -clcerts -nokeys -out observables/certs/user.crt
openssl pkcs12 -in certs/quickstart.p12 -nocerts -nodes -out observables/certs/user.key
```

This is the command that drives the pem-to-jks init container

```bash
openssl pkcs12 -export -inkey $keyFile -in $certFile -out $keystore_pkcs12 -password pass:$password && keytool -importkeystore -noprompt -srckeystore $keystore_pkcs12 -srcstoretype pkcs12 -destkeystore $keystore_jks -storepass $password -srcstorepass $password && cd /tmp/jks && csplit -z -f crt- $ca_bundle '/-----BEGIN CERTIFICATE-----/' '{*}' && for file in crt-*; do keytool -importcert -noprompt -keystore $truststore_jks -file $file -storepass $password -alias service-$file -storetype PKCS12; done"
```

An example of that is here (https://bitbucket.di2e.net/projects/YTM/repos/helm-charts/browse/ytm/ytmweb/templates/application/appdeployment.yaml)

