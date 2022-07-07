#!/usr/bin/env python3

## Linux Cluster
# database
config_db_linuxcluster = {
    'username': 'proyecto',
    'password': 'alianza',
    'host':     '10.20.12.161',  
    'database': 'proyecto'
}
# ssh
config_controller_lc = {
    'host': '10.20.12.161',
    'port':22,
    'username': 'grupo2',
    'private_key': './modulos/config/id_ecdsa',
    'passphrase': 'victor.bolivar@pucp.edu.pe'
}
config_w1_lc = {
    'host': '10.20.12.161',
    'port':2201,
    'username': 'w1',
    'private_key': './modulos/config/id_ecdsa',
    'passphrase': 'victor.bolivar@pucp.edu.pe'
}
config_w2_lc = {
    'host': '10.20.12.161',
    'port':2202,
    'username': 'w2',
    'private_key': './modulos/config/id_ecdsa',
    'passphrase': 'victor.bolivar@pucp.edu.pe'
}
config_w3_lc = {
    'host': '10.20.12.161',
    'port':2203,
    'username': 'wk3',
    'private_key': './modulos/config/id_ecdsa',
    'passphrase': 'victor.bolivar@pucp.edu.pe'
}
config_ofs_lc = {
    'host': '10.20.12.161',
    'port':2204,
    'username': 'ofs',
    'private_key': './modulos/config/id_ecdsa',
    'passphrase': 'victor.bolivar@pucp.edu.pe'
}

## Openstack
config_openstack = {
    'auth_url':'http://10.20.12.247:5000/v3',
    'project_name':'tel141',
    'username':'tel141',
    'password':'gabo',
    'user_domain_name':'Default',
    'project_domain_name':'Default'
}
config_db_openstack = {
    'username': 'proyecto',
    'password': 'proyecto',
    'host':     '10.20.12.247',  
    'database': 'proyecto'
}