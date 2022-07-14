#!/bin/bash

nombre=$1
ruta=$2
format=$3


export OS_PROJECT_DOMAIN_NAME=Default
export OS_USER_DOMAIN_NAME=Default
export OS_PROJECT_NAME=admin
export OS_USERNAME=admin
export OS_PASSWORD=gabo
export OS_AUTH_URL=http://control:5000/v3
export OS_IDENTITY_API_VERSION=3
export OS_IMAGE_API_VERSION=2

glance image-create --name $nombre --file $ruta --disk-format $format --container-format bare --visibility public