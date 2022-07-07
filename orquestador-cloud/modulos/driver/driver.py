#!/usr/bin/env python3

from cgitb import reset
from datetime import datetime, timedelta
from syslog import syslog
from prettytable import PrettyTable
#import pandas as pd
import csv

from .ssh import SSH
from .db import DB
from ..config.crendentials import config_controller_lc
from ..config.crendentials import config_db_linuxcluster
from ..config.crendentials import config_openstack

#import openstack
#openstack.enable_logging(debug=True, path='./modulos/logging/orquestador.log')


class Driver():
    def __init__(self) -> None:
        # Arquitectura#1 : Linux Cluster
        self.linuxc_db = DB(config_db_linuxcluster['host'],
                            config_db_linuxcluster['username'],
                            config_db_linuxcluster['password'],
                            config_db_linuxcluster['database'])
        self.linuxc_controller = SSH(config_controller_lc['host'],
                                     config_controller_lc['port'],
                                     config_controller_lc['username'],
                                     config_controller_lc['private_key'],
                                     config_controller_lc['passphrase'])
        self.linuxc_worker1 = SSH('10.20.12.107',
                                  2201,  # TODO
                                  'victor',
                                  config_controller_lc['private_key'],
                                  config_controller_lc['passphrase'])
        self.linuxc_worker2 = None
        self.linuxc_worker3 = None
        self.linuxc_ofs = None
        # Arquitectura#2 : OpenStack
        """ self.openstacksdk = openstack.connect(
                                auth_url=config_openstack['auth_url'],
                                project_name=config_openstack['project_name'],
                                username=config_openstack['username'],
                                password=config_openstack['password'],
                                user_domain_name=config_openstack['user_domain_name'],
                                project_domain_name=config_openstack['project_domain_name']) """

    # Linux Cluster: Scheduler

    def filter(self) -> list:
        # TODO
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
        list_cpu_usage = self.linuxc_worker1.list_cpu_usage(
            '/home/victor/worker1_cpu_metrics')
        worker1_cpu_avg = self.cpu_exponential_weigted_average(
            list_cpu_usage)  # exponential weigted average

        # lo mismo para los otros workers
        # se compara con el resto de workers
        worker_asignado = None
        return worker_asignado

    # Funciones

    def importar_imagen(self, data) -> dict:
        if (data['opcion'] == 1):
            # Subir archivo local
            # 1. Linux Cluster
            #self.linuxc_controller.subir_archivo(data['ruta'], '/home/grupo2/imagenes/'+data['categoria']+'/'+data['nombre'])
            # TODO actualizar db
            # TODO usar sdk para openstack
            print('\n[+] Imagen importada correctamente')
        elif(data['opcion'] == 2):
            # Subir desde URL
            # 1. Linux Cluster
            #self.linuxc_controller.ejecutar_comando('wget '+data['url']+' -O /home/grupo2/imagenes/'+data['categoria']+'/'+data['nombre'])
            # TODO actualizar db
            # TODO usar sdk para openstack
            print('\n[+] Imagen importada correctamente')
        return {
            'valor': 6,
            'mensaje': 'Imagen importada correctamente'
        }

    # Funciones pendientes

    def listar_topologias(self) -> None:
        x = PrettyTable()
        x.field_names = ["ID", "Nombre", "Tipo", "Infraestructura"]
        x.add_row([1, "Mi 1ra Topología", "Malla", "Linux Cluster"])
        x.add_row([2, "Primera Topología", "Lineal", "Linux Cluster"])
        x.add_row([3, "My first Topology", "Anillo", "Linux Cluster"])
        # Espaciado antes de imprimar la tabla
        x = '\n' + str(x)
        x = x.replace("\n", "\n                ")
        print(x)

    def topologia_json(self, topology_id) -> None:
        # verificar que sea un ID valido
        if(topology_id == 1):
            print('''
                                {
                                    "ID": 1,
                                    "Nombre": "Mi 1ra Topología",
                                    "Tipo": "Malla",
                                    "cantidad de enlaces": "4",
                                    "vlans"[
                                        {
                                            "idvlan":"1",
                                            "numeroVlan": "10",
                                            "red": "192.168.10.0/24"
                                            "dhcpServer": "192.168.10.2",
                                            "gateway": "192.168.10.1",
                                        },
                                        {
                                            "idvlan":"2",
                                            "numeroVlan": "20"
                                            "red": "192.168.20.0/24"
                                            "dhcpServer": "192.168.20.2",
                                            "gateway": "192.168.20.1",
                                        },
                                        {
                                            "idvlan":"3",
                                            "numeroVlan": "30"
                                            "red": "192.168.30.0/24"
                                            "dhcpServer": "192.168.30.2",
                                            "gateway": "192.168.30.1",
                                        },
                                    ]
                                    "cantidad de enlaces": "4",
                                    "vms": [
                                        {   
                                            "idVM": "12",
                                            "nombre": "vm80",
                                            "vlan": 10
                                            "ip": "192.168.10.10",
                                            "gateway": "192.168.10.1",
                                            "keypair": "key pair 1"
                                        },
                                        {   
                                            "idVM": "12",
                                            "nombre": "vm80",
                                            "vlan": 20
                                            "ip": "192.168.20.10",
                                            "gateway": 192.168.20.1,
                                            "keypair": "key pair 1"
                                        },
                                        {   
                                            "idVM" : "12",
                                            "nombre" : "vm80",
                                            "vlan": 30
                                            "ip": "192.168.30.10",
                                            "gateway": 192.168.30.1,
                                            "keypair" : "key pair 1"
                                        },
                                    ]
                                }                                 
                            ''')
        elif(topology_id == 2):
            print('''
                                {
                                    "ID": 1,
                                    "Nombre": "Primera Topología",
                                    "Tipo": "Malla",
                                    "dhcpServer": "x.x.x.x",
                                    "cantidad de enlaces": "4",
                                    "vlans"[
                                        {
                                            "idvlan":"1",
                                            "numeroVlan": "10"
                                        },
                                        {
                                            "idvlan":"2",
                                            "numeroVlan": "20"
                                        },
                                        {
                                            "idvlan":"3",
                                            "numeroVlan": "30"
                                        },
                                    ]
                                    "vms": [
                                        {   
                                            "idVM": "12",
                                            "nombre": "vm80",
                                            "vlan": 10
                                            "ip": "192.168.10.20",
                                            "gateway": "192.168.10.1",
                                            "keypair": "key pair 1"
                                        },
                                        {   
                                            "idVM": "12",
                                            "nombre": "vm80",
                                            "vlan": 20
                                            "ip": "192.168.20.20",
                                            "gateway": 192.168.20.1,
                                            "keypair": "key pair 1"
                                        },
                                        {   
                                            "idVM" : "12",
                                            "nombre" : "vm80",
                                            "vlan": 30
                                            "ip": "192.168.30.20",
                                            "gateway": 192.168.30.1,
                                            "keypair" : "key pair 1"
                                        },
                                    ]                                    
                                },                            
                            ''')
        elif(topology_id == 3):
            print('''
                                {
                                    "ID": 1,
                                    "Nombre": "My first Topology",
                                    "Tipo": "Malla",
                                    "gateway": "192.168.0.255",
                                    "dhcpServer": "x.x.x.x",
                                    "cantidad de enlaces": "4",
                                    "vlans"[
                                        {
                                            "idvlan":"1",
                                            "numeroVlan": "10"
                                        },
                                        {
                                            "idvlan":"2",
                                            "numeroVlan": "20"
                                        },
                                        {
                                            "idvlan":"3",
                                            "numeroVlan": "30"
                                        },
                                    ]
                                    "vms": [
                                        {   
                                            "idVM": "12",
                                            "nombre": "vm80",
                                            "vlan": 10
                                            "ip": "192.168.10.30",
                                            "gateway": "192.168.10.1",
                                            "keypair": "key pair 1"
                                        },
                                        {   
                                            "idVM": "12",
                                            "nombre": "vm80",
                                            "vlan": 20
                                            "ip": "192.168.20.30",
                                            "gateway": 192.168.20.1,
                                            "keypair": "key pair 1"
                                        },
                                        {   
                                            "idVM" : "12",
                                            "nombre" : "vm80",
                                            "vlan": 30
                                            "ip": "192.168.30.30",
                                            "gateway": 192.168.30.1,
                                            "keypair" : "key pair 1"
                                        },
                                    ]           
                                }
                            ''')

    def topologia_visualizador(self, topology_id) -> None:
        # TODO con el topology_id obtener de la DB la informacion
        # TODO se formatea a JSON para el modulo visualizacion (usar el json de la opcion1.3)
        # opciones "icon": unknown, switch, router, server, phone, host, cloud, firewall
        topologia_json_visualizador = {
            "nodes": [
                {
                    "id": 0,
                    "name": "PC0",
                    "icon": "host",
                    "Management": "192.168.0.10/24",
                    "vncLink": "https://tipo.vnrt/token=?"
                },
                {
                    "id": 1,
                    "name": "PC1",
                    "icon": "host",
                    "Management": "192.168.0.10/24",
                    "vncLink": "https://tipo.vnrt/token=?"
                },
                {
                    "id": 2,
                    "name": "PC2",
                    "icon": "host",
                    "Management": "192.168.0.10/24",
                    "vncLink": "https://tipo.vnrt/token=?"
                }
            ],
            "links": [
                {
                    "source": 0,
                    "target": 1,

                    "srcDevice": "PC0",
                    "tgtDevice": "PC1",

                    "srcIfName": "ens1",
                    "tgtIfName": "ens3"
                },
                {
                    "source": 0,
                    "target": 2,

                    "srcDevice": "PC0",
                    "tgtDevice": "PC2",

                    "srcIfName": "ens2",
                    "tgtIfName": "ens3"
                }
            ]
        }
        return topologia_json_visualizador

    def listar_imagenes(self) -> None:
        '''
            Funcion que imprime una tabla con las imagenes disponibles
        '''
        print(self.obtener_imagenes())

    def obtener_imagenes(self) -> str:
        '''
            Funcion que devuelve una tabla con las imagenes disponibles
        '''
        t = PrettyTable()
        t.field_names = ["ID", "Tipo de imagen", "Nombre"]
        t.add_row(["1", "Networking", "CiscoIoS"])
        t.add_row(["2", "Server", "CiscoIOS XRv"])
        t.add_row(["3", "Security", "Ubuntu 20.04"])
        t.add_row(["4", "Security", "Ubuntu 18.04"])
        t = str(t)
        t = '                '+str(t)
        t = t.replace("\n", "\n                ")
        return t

    def workers_info(self) -> dict:
        '''
            output
            ---
            workers_info:   se devuelve un diccionario con la informacion de los workers dentro de cada infraestructura
                            con el fin de que el usuario defina su AZ en el modulo validador

                            {
                                'openstack': tabla_openstack,
                                'linux_cluster': tabla_lc,
                            }

        '''
        # 1. tabla_openstack
        tabla_openstack = PrettyTable()
        tabla_openstack.field_names = ["ID", "Nombre", "Porcentaje de uso de CPU", "cantidad disponible de vCPU",
                                       "cantidad de memoria libre", "cantidad de disco libre"]
        tabla_openstack.add_row(
            ["1001", "Worker1", "30 %", 16, "3 GB", "20 GB"])
        tabla_openstack.add_row(
            ["1002", "Worker2", " 50 %", 10, "2 GB", "15 GB"])
        tabla_openstack.add_row(
            ["1003", "Worker3", " 60 %", 12, "2 GB", "10 GB"])
        tabla_openstack = str(tabla_openstack)
        tabla_openstack = '                '+tabla_openstack
        tabla_openstack = tabla_openstack.replace("\n", "\n                ")
        # 2. tabla_lc
        tabla_lc = PrettyTable()
        tabla_lc.field_names = ["ID", "Nombre", "Porcentaje de uso de CPU", "cantidad disponible de vCPU",
                                "cantidad de memoria libre", "cantidad de disco libre"]
        tabla_lc.add_row(["1", "Worker1", "30 %", 16, "3 GB", "20 GB"])
        tabla_lc.add_row(["2", "Worker2", " 50 %", 10, "2 GB", "15 GB"])
        tabla_lc.add_row(["3", "Worker3", " 60 %", 12, "2 GB", "10 GB"])
        tabla_lc = str(tabla_lc)
        tabla_lc = '                '+tabla_lc
        tabla_lc = tabla_lc.replace("\n", "\n                ")

        return {
            'openstack': tabla_openstack,
            'linux_cluster': tabla_lc
        }

    def separar_recursos_topologia(self, nueva_topologia) -> list:
        '''
            Dada la informacion ingresada por el usuario, se verifica que existan los recursos suficientes 
            haciendo la consulta a la DB de la infraestructura correspondiente.

            De ser asi, se procederia a separar los recursos y se retorna un 'True'. 
            Sino, se retorna un 'False' indicando que no existen los recursos suficientes.

            inputs
            ---
                nueva_topologia (dict): diccionario que almacena la informacion de la topologia a separar.
            
            outputs
            ---
                recursos_suficientes (bool): booleano que indica si existen los recursos sufientes.
                result (dict): resultado de la operacion con el fin de loggear las operaciones realizadas
            
        '''
        recursos_suficientes = True
        print('[+] Recursos separados correctamente en la base de datos')
        result = {
            'valor': 6,
            'mensaje': 'Recursos separados correctamente en la base de datos'
        }

        return [recursos_suficientes, result]
    
    def separar_recursos_nodo(self, nuevo_nodo) -> list:
        '''
            Dada la informacion ingresada por el usuario, se verifica que existan los recursos suficientes 
            haciendo la consulta a la DB de la infraestructura correspondiente.

            De ser asi, se procederia a separar los recursos y se retorna un 'True'. 
            Sino, se retorna un 'False' indicando que no existen los recursos suficientes.

            inputs
            ---
                nuevo_nodo (dict): diccionario que almacena la informacion del nodo a separar.
            
            outputs
            ---
                recursos_suficientes (bool): booleano que indica si existen los recursos sufientes.
                result (dict): resultado de la operacion con el fin de loggear las operaciones realizadas
            
        '''
        recursos_suficientes = True
        print('[+] Recursos separados correctamente en la base de datos')
        result = {
            'valor': 6,
            'mensaje': 'Recursos separados correctamente en la base de datos'
        }

        return [recursos_suficientes, result]

    def listar_workers_actuales(self, id_topologia) -> None:
        print('Actualmente su topologia cuenta con: '+str(['worker1', 'worker2']))
        print()

    def workers_info_slice(self, id_topologia) -> str:
        '''
            A apartir del ID de una topologia, se define que tipo de infraestructura usa y se 
            devuelve la tabla para esa infraestructura.
        '''
        return self.workers_info()['openstack']

    def crear_topologia(self, nueva_topologia) -> dict:
        print('[+] Se creó correctamente')
        result = {
            'valor': 6,
            'mensaje': 'Topologia creada correctamente'
        }
        return result

    def eliminar_topologia(self, id_topologia) -> dict:
        print('\n[-] Se eliminó correctamente')
        return {
            'valor': 6,
            'mensaje': 'Topologia eliminada correctamente'
        }

    def crear_vm(self, data) -> dict:
        print('[+] VM creada correctamente')
        result = None  # codigo sislog
        return result

    def agregar_nodo(self, data) -> dict:
        print('[+] Se agregó correctamente')
        result = {
            'valor': 6,
            'mensaje': 'Maquina virtual creada satisfactoriamente'
        }
        return result

    def listar_nodos(self, id_topologia) -> None:
        t = PrettyTable()
        t.field_names = ["ID",  "Nombre"]
        t.add_row(["1", "Nodo 1"])
        t.add_row(["2", "Nodo 2"])
        t.add_row(["3", "Nodo 3"])
        t.add_row(["4", "Nodo 4"])
        t = '\n' + str(t)
        t = t.replace("\n", "\n                ")
        print(t)

    def eliminar_nodo(self, id_topologia, id_nodo) -> dict:
        print('\n[-] Se eliminó correctamente')
        result = {
            'valor': 6,
            'mensaje': 'Maquina virtual eliminada satisfactoriamente'
        }
        return result

    def aumentar_slice(self, data) -> dict:
        print('\n[+] Slice aumentado exitosamente')
        result = {
            'valor': 6,
            'mensaje': 'Slice aumentado exitosamente'
        }
        return result

    def conectar_nodo_internet(self, id_nodo) -> dict:
        print('\n[+] Conexión exitosa')
        return {
            'valor': 6,
            'mensaje': 'Conexion de nodo a internet satisfactoria'
        }

    def conectar_topologias(self, id_topologia1, id_topologia2) -> dict:
        print('\n[+] Conexión exitosa')
        return {
            'valor': 6,
            'mensaje': 'Conexion entre slices satisfactorio'
        }
