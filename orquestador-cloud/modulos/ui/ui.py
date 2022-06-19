#!/usr/bin/env python3

from ..logging.Exceptions import InputException

from ..validador.validador import obtener_int
from ..validador.validador import obtener_tipo_topologia
from ..validador.validador import obtener_infraestructura

from ..validador.validador import obtener_numero_vcpus
from ..validador.validador import obtener_memoria
from ..validador.validador import obtener_fs
from ..validador.validador import obtener_imagen
from ..validador.validador import input_crear_topologia

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

                1.1 Tabla resumen de todas las topologias
                1.2 JSON con detalle de una topologia en particular
                1.3 Grafico de topologia en particular
                1.4 Listar images disponibles
                1.6 Listar key pair
                1.5 Regresar
            ''')
        opcion = obtener_int('Ingrese la opcion: ', minValor=1, maxValor=5)
        if(opcion):
            if (opcion == 1):
                # TODO se lista topologias Linux Cluster
                self.db_linuxc.obtener_topologias()
                # TODO se lista topologias Openstack
                pass
            elif (opcion == 2):
                # TODO
                pass
            elif (opcion == 3):
                # TODO
                pass
            elif (opcion == 4):
                self.grafico_topologia()
            elif (opcion == 5):
                # TODO
                pass
            elif (opcion == 6):
                pass
        else:
            # Si no se especifico una opcion valida, se procede con el bucle
            print('[x] Ingrese una opcion valida')
            
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

            # TODO se pide el numero de vms a crear y para cada vm se piden los siguentes datos
            n_vcpus = obtener_numero_vcpus()
            memoria = obtener_memoria()
            # fs = obtener_fs()
            # imagen = obtener_imagen()

            # TODO preguntar que VLANs desea inteconectar

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

                1.1 Borrar topologia
                1.2 Añadir nodo en topologia
                1.3 Eliminar nodo en topologia
                1.4 Aumentar capacidad de slice 
                1.5 Editar conectividad
                1.6 Añadir imagen 
                1.7 Añadir keypair
                1.8 Regresar
            ''')
        opcion = obtener_int('Ingrese la opcion: ', minValor=1, maxValor=7)
        if(opcion):
            if (opcion == 1):
                # TODO
                pass
            elif (opcion == 2):
                # TODO
                pass
            elif (opcion == 3):
                # TODO
                pass
            elif (opcion == 4):
                # TODO: Aumentar capacidad de slice (añadir mas workers)
                pass
            elif (opcion == 5):
                # TODO
                pass
            elif (opcion == 6):
                data = obtener_imagen() # MODULO: VALIDACION
                result = self.enlace.importar_imagen(data) # MODULO: ENLACE
                # TODO pasar el result al modulo logging para general el log
            elif (opcion == 7):
                # TODO
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
            opcion = obtener_int('Ingrese la opcion: ', minValor=1, maxValor=4)
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