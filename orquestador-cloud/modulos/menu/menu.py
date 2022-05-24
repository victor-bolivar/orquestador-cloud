#!/usr/bin/env python3

from ..validador.validador import obtener_int
import sys
import json
import webbrowser

class Menu:
    def __init__(self):
        self.topologias = [] # TODO se pasara la data obtenida de la db
        pass

    ## Opciones del menu principal

    # Opcion 1

    def opcion_1(self):
        print('''
            -----------------------------------------------------------------------------

            1. Listar topologias existentes

                1.1 Tabla resumen de todas las topologias
                1.2 Tabla con detalle de una topologia en particular
                1.3 JSON con detalle de una topologia en particular
                1.4 Grafico de topologia en particular
                1.5 Regresar
            ''')
        opcion = obtener_int('[?] Ingrese la opcion: ', minValor=1, maxValor=5)
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
                self.grafico_topologia()
            elif (opcion == 5):
                pass
        else:
            # Si no se especifico una opcion valida, se procede con el bucle
            print('[x] Ingrese una opcion valida')
            
    def grafico_topologia(self):
        id = input('[?] Ingrese el ID de la topologia: ') 
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

        # TODO se guarda en ./modulos/visualizador/data.json
        header = "\n\nvar topologyData = "
        with open('modulos/visualizador/data.js', 'w') as data_json:
            data_json.write(header)
            data_json.write(json.dumps(topologia_json, indent=4, sort_keys=True))
            data_json.write(';')
        
        # TODO se abre el browser para visualizar la topologia
        webbrowser.open_new_tab('modulos/visualizador/app.html')

    # Metodo principal

    def iniciar_menu(self):
        while True:
            print('''
            -----------------------------------------------------------------------------

                1. Listar topologias existentes
                2. Crear nueva topologia
                3. Editar topologia
                4. Salir
            ''')
            opcion = obtener_int('[?] Ingrese la opcion: ', minValor=1, maxValor=4)
            if(opcion):
                if (opcion == 1):
                    self.opcion_1()
                elif (opcion == 2):
                    # TODO
                    pass
                elif (opcion == 3):
                    # TODO
                    pass
                elif (opcion == 4):
                    sys.exit(0)
            else:
                print('[x] Ingrese una opcion valida')
                # Si no se especifico una opcion valida, se procede con el bucle
                continue