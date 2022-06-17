#!/usr/bin/env python3

# databases
config_db_linuxcluster = {
    'username': 'proyecto',
    'password': 'alianza',
    'host':     '10.20.12.161',  
    'database': 'proyecto1'
}

# ssh
controller_lc = {
    'host': '10.20.12.161',
    'port':22,
    'username': 'grupo2',
    'private_key': './modulos/config/id_ecdsa',
    'passphrase': 'victor.bolivar@pucp.edu.pe'
}