#!/usr/bin/env python3

from ..logging.Exceptions import InputException

from prettytable import PrettyTable
from ..validador.validador import obtener_int
from ..validador.validador import obtener_tipo_topologia
from ..validador.validador import obtener_infraestructura

from ..validador.validador import obtener_numero_vcpus
from ..validador.validador import obtener_memoria
from ..validador.validador import obtener_fs
from ..validador.validador import obtener_imagen
from ..validador.validador import input_crear_topologia
from ..validador.validador import id_topologia_eliminar
from ..validador.validador import id_topologia_nodo_adicional
from ..validador.validador import validar_eliminar_nodo
from ..validador.validador import validar_aumentar_slice
from ..validador.validador import validar_conectividad
from ..validador.validador import validar_keypair
from ..validador.validador import obtener_almacenamiento
from ..validador.validador import obtener_imagenvm
from ..validador.validador import obtener_keypair
from ..validador.validador import conectar_internet
from ..enlace.enlace import Enlace

import sys
import json
import webbrowser

class UI:
    def __init__(self):
        self.enlace = Enlace()
    ## Opciones del menu principal

    # Opcion 1

    def opcion_1(self):
        print('''
            -----------------------------------------------------------------------------

            1. Listar informacion

                1. Tabla resumen de todas las topologías
                2. JSON con detalle de una topología en particular
                3. Gráfico de topología en particular
                4. Listar imágenes disponibles
                5. Listar Key Pair
                6. Regresar

            ''')
        opcion = obtener_int('Ingrese la opcion: ', minValor=1, maxValor=5)
        if(opcion):
            if (opcion == 1):

                x = PrettyTable()
                x.field_names = ["ID", "Nombre", "Tipo", "Infraestructura"]
                x.add_row([1, "Mi 1ra Topología", "Malla", "Linux Cluster"])
                x.add_row([2, "Primera Topología", "Lineal", "Linux Cluster"])
                x.add_row([3, "My first Topology", "Anillo", "Linux Cluster"])
                #Espaciado antes de imprimar la tabla
                x = '\n'+ str(x)
                x = x.replace("\n", "\n                ")
                print(x)

            
                
            elif (opcion == 2):
                vart = True
                while vart:
                    opcion_detalle = obtener_int('Ingrese el ID de la Topología: ', minValor=1, maxValor=3)
                    if (opcion_detalle):
                        if(opcion_detalle==1):
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
                            break
                        if(opcion_detalle==2):
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
                            break
                        if(opcion_detalle==3):
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
                            break
                            
                    else:
                        print('[x] Ingrese una opción válida: ')
                
            elif (opcion == 3):
                self.grafico_topologia()

            elif (opcion == 4):
                #############
                #print('''
                #    -----------------------------------------------------------------------------
                #    Lista de imágenes sisponibles

                #''')
                x3 = PrettyTable()
                x3.field_names = ["ID","Tipo de imagen", "Nombre"]
                x3.add_row(["1", "Networking", "CiscoIoS"])
                x3.add_row(["2","Server", "CiscoIOS XRv"])
                x3.add_row(["3","Security", "Ubuntu 20.04"])
                x3.add_row(["4","Security", "Ubuntu 18.04"])
                #print()
                x3 = '\n'+ str(x3)
                x3 = x3.replace("\n", "\n                ")
                #print(x)
                print(x3)
                
            elif (opcion == 5):
                x = PrettyTable()
                x.field_names = ["ID", "Nombre"]
                x.add_row([1, "key pair 1"])
                x.add_row([2, "key pair 2"])
                x.add_row([3, "key pair 3"])
                #Espaciado antes de imprimar la tabla
                x = '\n'+ str(x)
                x = x.replace("\n", "\n                ")
                print(x)

            elif (opcion == 6):
                pass
        else:
            # Si no se especifico una opcion valida, se procede con el bucle
            print('[x] Ingrese una opción válida')
            
    def grafico_topologia(self):
        # TODO mostrar tabla con datos: idTopologia y nombreTopologia
        id = input('Ingrese el ID de la topologia: ') 
        # TODO validar que sea un ID valido (int o string)
        # TODO validar que exista el ID

        # TODO con el ID se obtiene la topologia buscada dentro de self.topologies
        topologia_json = {
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

        # TODO se formatea a JSON para el modulo visualizacion (usar el json de la opcion1.3)
        # opciones "icon": unknown, switch, router, server, phone, host, cloud, firewall

        # se guarda en ./modulos/visualizador/data.json
        header = "\n\nvar topologyData = "
        with open('modulos/visualizador/data.js', 'w') as data_json:
            data_json.write(header)
            data_json.write(json.dumps(topologia_json, indent=4, sort_keys=True))
            data_json.write(';')
        
        # se abre el browser para visualizar la topologia
        webbrowser.open_new_tab('modulos/visualizador/app.html')

    # Opcion 2

    def opcion_2(self):
        # TODO se rellenaria un objeto de Topologia con los atributos obtenidos
        tipo_topologia = None
        infraestructura = None

        try:
            print() # se imprime nueva linea en menu
            tipo_topologia = obtener_tipo_topologia()
            infraestructura = obtener_infraestructura()
            conexion = conectar_internet()

            # TODO se pide el numero de vms a crear y para cada vm se piden los siguentes datos
            print()
            print('A continuación se le pedirá definir las capacidades de las 3 VM')
            print('')
            print('---------------------Configuración de la VM 1-----------------------------\n')
            n_vcpus = obtener_numero_vcpus()
            memoria = obtener_memoria()
            almacenamiento = obtener_almacenamiento()
            imagen = obtener_imagenvm()
            keypair1 = obtener_keypair()
            
            # fs = obtener_fs()
            # imagen = obtener_imagen()

            # TODO preguntar que VLANs desea inteconectar
            print('')
            print('---------------------Configuración de la VM 2-----------------------------\n')
            n_vcpus = obtener_numero_vcpus()
            memoria = obtener_memoria()
            almacenamiento = obtener_almacenamiento()
            imagen = obtener_imagenvm()
            keypair2 = obtener_keypair()

            print('')
            print('---------------------Configuración de la VM 3-----------------------------\n')
            n_vcpus = obtener_numero_vcpus()
            memoria = obtener_memoria()
            almacenamiento = obtener_almacenamiento()
            imagen = obtener_imagenvm()
            keypair3 = obtener_keypair()
            topo = self.enlace.crear_topologia(keypair3)

        except InputException as inputException:
            print(inputException)
            return

        # TODO mostrar resumen de informacion ingresa para que el usuario confirme

        # TODO se crean las VMs usando el modulo correspondiente

    # Opcion 3

    def opcion_3(self):
        print('''
            -----------------------------------------------------------------------------

            3. Editar informacion

                1.1 Borrar topología
                1.2 Añadir nodo en topología
                1.3 Eliminar nodo en topología
                1.4 Aumentar capacidad de slice 
                1.5 Editar conectividad
                1.6 Añadir imagen 
                1.7 Añadir keypair
                1.8 Regresar
            ''')
        opcion = obtener_int('Ingrese la opción: ', minValor=1, maxValor=7)
        if(opcion):
            if (opcion == 1):
                # TODO
                borrado = id_topologia_eliminar()
                eliminar = self.enlace.eliminar_topologia(borrado)
                pass
            elif (opcion == 2):
                agre = id_topologia_nodo_adicional()
                agregar = self.enlace.agregar_nodo(agre)
                pass
            elif (opcion == 3):
                # TODO
                nodo = validar_eliminar_nodo()
                eliminar_nodo = self.enlace.eliminar_nodo(nodo)
                pass
            elif (opcion == 4):
                # TODO: Aumentar capacidad de slice (añadir mas workers)
                slice = validar_aumentar_slice()
                eliminar_nodo = self.enlace.aumentar_slice(slice)
                pass
            elif (opcion == 5):
                conectividad = validar_conectividad()
                conectar_slice_internet =self.enlace.conectar_slice_internet(conectividad)
                # TODO
                pass
            elif (opcion == 6):
                data = obtener_imagen() # MODULO: VALIDACION
                result = self.enlace.importar_imagen(data) # MODULO: ENLACE
                # TODO pasar el result al modulo logging para general el log
            elif (opcion == 7):
                # TODO
                keypair = validar_keypair()
                agregar_keypair =self.enlace.agregar_key_apir(keypair)
                pass
            elif (opcion == 8):
                pass
        else:
            # Si no se especifico una opcion valida, se procede con el bucle
            print('[x] Ingrese una opcion valida')


    # Metodo principal

    def iniciar_menu(self):
        while True:
            print('''
            -----------------------------------------------------------------------------

                1. Listar informacion
                2. Crear nueva topologia
                3. Editar informacion
                4. Salir
            ''')
            opcion = obtener_int('Ingrese la opción: ', minValor=1, maxValor=4)
            if(opcion):
                if (opcion == 1):
                    self.opcion_1()
                elif (opcion == 2):
                    self.opcion_2()
                elif (opcion == 3):
                    self.opcion_3()
                elif (opcion == 4):
                    sys.exit(0)
            else:
                print('[x] Ingrese una opcion valida')
                # Si no se especifico una opcion valida, se procede con el bucle
                continue