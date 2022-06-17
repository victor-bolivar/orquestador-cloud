#!/usr/bin/env python3

from .ssh import SSH
from .db import DB

from ..config.crendentials import controller_lc
from ..config.crendentials import config_db_linuxcluster

class Enlace():
    def __init__(self) -> None:
        # Arquitectura#1 : Linux Cluster
        self.linuxc_db = DB(config_db_linuxcluster['host'], 
                                    config_db_linuxcluster['username'], 
                                    config_db_linuxcluster['password'], 
                                    config_db_linuxcluster['database'])
        self.linuxc_controller = SSH(  controller_lc['host'], 
                            controller_lc['port'], 
                            controller_lc['username'],
                            controller_lc['private_key'],
                            controller_lc['passphrase'])
        self.linuxc_worker1 = None
        self.linuxc_worker2 = None
        self.linuxc_worker3 = None
        self.linuxc_ofs = None
        # Arquitectura#2 : OpenStack
        self.openstacksdk = None 

    # Funciones particulares

    def importar_imagen(self, data):
        if (data['opcion']==1):
            # Subir archivo local
            # 1. Linux Cluster
            self.linuxc_controller.subir_archivo(data['ruta'], '/home/grupo2/imagenes/'+data['categoria']+'/'+data['nombre'])
            # TODO actualizar db
            # TODO usar sdk para openstack
            print('[+] Imagen importada correctamente')
        elif(data['opcion']==2):
            # Subir desde URL
            # 1. Linux Cluster
            self.linuxc_controller.ejecutar_comando('wget '+data['url']+' -O /home/grupo2/imagenes/'+data['categoria']+'/'+data['nombre'])
            # TODO actualizar db
            # TODO usar sdk para openstack
            print('[+] Imagen importada correctamente')

    def crear_vm(self, infraestructura):
        if infraestructura == 1:
            # creacion en linux cluster
            pass
        elif infraestructura == 2:
            # creacion openstack
            pass
        # si se quiere añadir un nuevo tipo de infraestructura, se implementaria aca

