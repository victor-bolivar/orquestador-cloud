#!/usr/bin/env python3

from datetime import datetime, timedelta
#import pandas as pd
import csv

from .ssh import SSH
from .db import DB
from ..config.crendentials import config_controller_lc
from ..config.crendentials import config_db_linuxcluster
from ..config.crendentials import config_openstack

""" import openstack
openstack.enable_logging(debug=True, path='./modulos/logging/orquestador.log') """

class Enlace():
    """ def __init__(self) -> None:
        # Arquitectura#1 : Linux Cluster
        self.linuxc_db = DB(config_db_linuxcluster['host'], 
                                    config_db_linuxcluster['username'], 
                                    config_db_linuxcluster['password'], 
                                    config_db_linuxcluster['database'])
        self.linuxc_controller = SSH(  config_controller_lc['host'], 
                            config_controller_lc['port'], 
                            config_controller_lc['username'],
                            config_controller_lc['private_key'],
                            config_controller_lc['passphrase'])
        self.linuxc_worker1 = SSH(  '10.20.12.107', 
                            2201, # TODO
                            'victor',
                            config_controller_lc['private_key'],
                            config_controller_lc['passphrase'])
        self.linuxc_worker2 = None
        self.linuxc_worker3 = None
        self.linuxc_ofs = None
        # Arquitectura#2 : OpenStack
        self.openstacksdk = openstack.connect(
                                auth_url=config_openstack['auth_url'],
                                project_name=config_openstack['project_name'],
                                username=config_openstack['username'],
                                password=config_openstack['password'],
                                user_domain_name=config_openstack['user_domain_name'],
                                project_domain_name=config_openstack['project_domain_name']) """

    # Funciones: listar
    def listar_imagenes(self):
        # TODO Linux Cluster
        # TODO Openstack
        print("List Images:")
        for image in self.openstacksdk.image.images():
            print(image)

    # Funciones 

    def importar_imagen(self, data):
        if (data['opcion']==1):
            # Subir archivo local
            # 1. Linux Cluster
            #self.linuxc_controller.subir_archivo(data['ruta'], '/home/grupo2/imagenes/'+data['categoria']+'/'+data['nombre'])
            # TODO actualizar db
            # TODO usar sdk para openstack
            print('[+] Imagen importada correctamente')
        elif(data['opcion']==2):
            # Subir desde URL
            # 1. Linux Cluster
            #self.linuxc_controller.ejecutar_comando('wget '+data['url']+' -O /home/grupo2/imagenes/'+data['categoria']+'/'+data['nombre'])
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

    # Linux Cluster: Filter y Scheduler

    def filter(self) -> list:
        # se devuelve la lista de workers validos para almacenar una vm con los requisitos
        pass

    def cpu_exponential_weigted_average(self, data):
        '''
            Se devuelve el uso promedio (%) calculado en base a Exponential Moving Average,
            lo que le da mas peso a las ultima metricas

            https://www.geeksforgeeks.org/how-to-calculate-an-exponential-moving-average-in-python/

            inputs
            ---
            data: lista con los usos (ex:[80,60,50,20])
        '''
        # create a dataframe
        cpu_metrics = pd.DataFrame({'cpu_usage': data})
        # finding EMA
        ema = cpu_metrics.ewm(alpha=0.5).mean()
        return ema["cpu_usage"].iloc[-1]
    
    def coeficiente_carga(self):
        pass

    def scheduler_cluster_linux(self):  
        # TODO
        # obtener metricas de worker1
        # exponential weigted average
        # calcular coeficiente de carga

        # Worker 1
        list_cpu_usage = self.linuxc_worker1.list_cpu_usage('/home/victor/worker1_cpu_metrics')
        worker1_cpu_avg = self.cpu_exponential_weigted_average(list_cpu_usage) # exponential weigted average

        # lo mismo para los otros workers
        # se compara con el resto de workers
        worker_asignado = None
        return worker_asignado
    
    # Funciones pendientes
    def crear_topologia(self, data):
        print('[+] Se creó correctamente')
        

    def eliminar_topologia(self, borrado):
        print('[-] Se eliminó correctamente')
    
    def agregar_nodo(self, agregar):
        print('[+] Se agregó correctamente')
    
    def eliminar_nodo(self, nodo):
        print('[-] Se eliminó correctamente')
    
    def aumentar_slice(self, slice):
        print('[+] Agregado exitosamente')
    
    def conectar_slice_internet(self, slice):
        print('[+] Conexión exitosa')

    def agregar_key_apir(self, keypair):
        print('[+] Key importada correctamente')

        