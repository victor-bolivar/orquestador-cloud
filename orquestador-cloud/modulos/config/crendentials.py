#!/usr/bin/env python3

## Linux Cluster
# database
config_db_linuxcluster = {
    'username': 'proyecto',
    'password': 'alianza',
    'host':     '10.20.12.161',  
    'database': 'proyecto1'
}
# ssh
config_controller_lc = {
    'host': '10.20.12.161',
    'port':22,
    'username': 'grupo2',
    'private_key': './modulos/config/id_ecdsa',
    'passphrase': 'victor.bolivar@pucp.edu.pe'
}

## Openstack
config_openstack = {
    'auth_url':'http://controller:5000/v3',
    'project_name':'tel141',
    'username':'tel141',
    'password':'alianza',
    'user_domain_name':'Default',
    'project_domain_name':'Default'
}
