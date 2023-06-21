#!/bin/sh

printf "Generating localhost SMTP SSL certificate...\n"

ls localhost.crt > /dev/null 2>&1 && ls localhost.key > /dev/null 2>&1 || \
    openssl req \
        -x509 \
        -out localhost.crt \
        -keyout localhost.key \
        -newkey rsa:2048 \
        -nodes \
        -sha256 \
        -subj '/CN=localhost' \
        -extensions EXT \
        -config openssl.cfg
