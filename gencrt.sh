openssl genrsa -out pmail.key 1024
openssl rsa -noout -text -in pmail.key
openssl rsa -in pmail.key -out pmail.key.unsecure
openssl req -new -x509 -nodes -sha1 -days 365 -key pmail.key -out pmail.crt
openssl x509 -noout -text -in pmail.crt

