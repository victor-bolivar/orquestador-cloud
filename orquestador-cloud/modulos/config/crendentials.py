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
    'OS_AUTH_URL':'http://10.20.12.247:5000/v3',
    'COMPUTE_URL': "http://10.20.12.247:8774/v2.1",
    'NETWORK_URL': "http://10.20.12.247:9696",
    'GLANCE_URL': 'http://10.20.12.247:9292',
    'OS_PROJECT_NAME':'admin',
    'OS_USERNAME':'admin',
    'OS_PASSWORD':'gabo',
    'OS_USER_DOMAIN_NAME':'Default',
    'OS_PROJECT_DOMAIN_NAME':'Default'
}
config_db_openstack = {
    'username': 'proyecto',
    'password': 'proyecto',
    'host':     '10.20.12.247',  
    'database': 'proyecto'
}
# ssh
config_controller_openstack = {
    'host': '10.20.12.247',
    'port':22,
    'username': 'proyecto',
    'private_key': './modulos/config/id_ecdsa',
    'passphrase': 'victor.bolivar@pucp.edu.pe'
}
config_w1_openstack = {
    'host': '10.20.12.247',
    'port':2201,
    'username': 'worker',
    'private_key': './modulos/config/id_ecdsa',
    'passphrase': 'victor.bolivar@pucp.edu.pe'
}
config_w2_openstack = {
    'host': '10.20.12.247',
    'port':2202,
    'username': 'worker',
    'private_key': './modulos/config/id_ecdsa',
    'passphrase': 'victor.bolivar@pucp.edu.pe'
}
config_w3_openstack = {
    'host': '10.20.12.247',
    'port':2203,
    'username': 'worker',
    'private_key': './modulos/config/id_ecdsa',
    'passphrase': 'victor.bolivar@pucp.edu.pe'
}