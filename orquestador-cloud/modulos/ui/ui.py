#!/usr/bin/env python3

from ..logging.Exceptions import InputException
from ..validador.validador import Validador
from ..enlace.enlace import Enlace

import sys
import json
import webbrowser
from prettytable import PrettyTable


class UI:
    def __init__(self):
        self.enlace = Enlace()
        self.validador = Validador()

    # Opciones del menu principal

    # Opcion 1

    def opcion_1(self):
        print('''
            -----------------------------------------------------------------------------

            1. Listar informacion

                1. Tabla resumen de todas las topologías
                2. JSON con detalle de una topología en particular
                3. Gráfico de topología en particular
                4. Listar imágenes disponibles
                5. Regresar

            ''')
        opcion = self.validador.obtener_int(
            'Ingrese la opcion: ', minValor=1, maxValor=5)
        if(opcion):
            if (opcion == 1):
                self.enlace.listar_topologias()

            elif (opcion == 2):
                self.enlace.listar_topologias()
                print()  # print new line
                topology_id = self.validador.obtener_int(
                    'Ingrese el ID de la Topología: ', minValor=1, maxValor=3)
                if(topology_id):
                    result = self.enlace.topologia_json(topology_id)
                    # TODO pasar el result al modulo logging
                else:
                    print('[x] Ingrese una opción válida')

            elif (opcion == 3):
                self.enlace.listar_topologias()
                print()  # print new line
                topology_id = self.validador.obtener_int(
                    'Ingrese el ID de la Topología: ', minValor=1, maxValor=3)
                if(topology_id):
                    [topologia_json_visualizador, result] = self.enlace.topologia_visualizador(
                        topology_id)

                    # se guarda en ./modulos/visualizador/data.json
                    header = "\n\nvar topologyData = "
                    with open('modulos/visualizador/data.js', 'w') as data_json:
                        data_json.write(header)
                        data_json.write(json.dumps(
                            topologia_json_visualizador, indent=4, sort_keys=True))
                        data_json.write(';')
                    # se abre el browser para visualizar la topologia
                    webbrowser.open_new_tab('modulos/visualizador/app.html')

                    # TODO logging con el codigo syslog en 'result'
                else:
                    print('[x] Ingrese una opción válida')

            elif (opcion == 4):
                print()
                result = self.enlace.listar_imagenes()
                # TODO logging

            elif (opcion == 5):
                pass
        else:
            # Si no se especifico una opcion valida, se procede con el bucle
            print('[x] Ingrese una opción válida')

    # Opcion 2

    def opcion_2(self):
        try:
            workers_info = self.enlace.workers_info()
            imagenes = self.enlace.obtener_imagenes()
            nueva_topologia = self.validador.nueva_topologia(
                workers_info, imagenes)

            # TODO validar recursos en DB y separarlos
            print('A continuacion se muestra la configuracion ingresada: \n')
            topology_json = json.dumps(nueva_topologia, indent=4)
            topology_json = '                '+topology_json
            topology_json = topology_json.replace("\n", "\n                ")
            print(topology_json)

            opcion = self.validador.obtener_int(
                '\n¿Desea proceder con la creacion de la topologia? (1. Si | 2. No): ')
            print()
            if (opcion == 1):
                self.enlace.crear_topologia(nueva_topologia)
            elif (opcion == 2):
                print('[-] No se realizo la creacion de la topologia')
            else:
                print('[x] Ingrese una opcion valida')
        except InputException as inputException:
            print(inputException)
            return

    # Opcion 3

    def opcion_3(self):
        print('''
            -----------------------------------------------------------------------------

            3. Editar informacion

                3.1 Borrar topología
                3.2 Añadir nodo en topología
                3.3 Eliminar nodo en topología
                3.4 Aumentar capacidad de slice 
                3.5 Conexion a internet
                3.6 Añadir imagen 
                3.7 Regresar
            ''')
        opcion = self.validador.obtener_int(
            'Ingrese la opción: ', minValor=1, maxValor=7)
        if(opcion):
            if (opcion == 1):
                self.enlace.listar_topologias()
                id_topologia = self.validador.obtener_int('\nIngrese el ID: ')
                result = self.enlace.eliminar_topologia(id_topologia)
                # TODO logging

            elif (opcion == 2):
                # se lista y obtiene informacion del estado actual del orquestados
                self.enlace.listar_topologias()
                tabla_imagenes = self.enlace.obtener_imagenes()

                # se obtiene la data del usuario para la creacion de la VM
                data = self.validador.agregar_nodo(tabla_imagenes)

                # TODO validar que existen recursos suficientes en la DB y separarlos

                # se pide al usuario confirmar la informacion ingresada
                print('A continuacion se muestra la configuracion ingresada: \n')
                data_json = json.dumps(data, indent=4)
                data_json = '                '+data_json
                data_json = data_json.replace("\n", "\n                ")
                print(data_json)
                opcion = self.validador.obtener_int(
                    '\n¿Desea proceder con la creacion del nodo? (1. Si | 2. No): ')
                print()
                if (opcion == 1):
                    result = self.enlace.agregar_nodo(data)
                    # TODO logging
                elif (opcion == 2):
                    print('[-] No se realizo la creacion del nodo')
                else:
                    print('[x] Ingrese una opcion valida')

            elif (opcion == 3):
                self.enlace.listar_topologias()
                id_topologia = self.validador.obtener_int(
                    '\nIngrese el ID de la topologia: ')
                self.enlace.listar_nodos(id_topologia)
                id_nodo = self.validador.obtener_int(
                    '\nIngrese el ID del nodo: ')
                result = self.enlace.eliminar_nodo(id_topologia, id_nodo)
                # TODO logging de eliminar

            elif (opcion == 4):
                self.enlace.listar_topologias()
                id_topologia = self.validador.obtener_int(
                    '\nIngrese el ID de la topologia: ')
                print()
                # TODO listar los workers actuales en la topologia
                workers_info = self.enlace.workers_info()
                data = self.validador.aumentar_slice(workers_info)
                result = self.enlace.aumentar_slice(data)
                # TODO logging

            elif (opcion == 5):

                self.enlace.listar_topologias()
                id_topologia = self.validador.obtener_int(
                    '\nIngrese el ID de la topologia: ')
                result = self.enlace.conectar_slice_internet(id_topologia)
                # TODO: logging

            elif (opcion == 6):
                data = self.validador.importar_imagen()  # MODULO: VALIDACION
                result = self.enlace.importar_imagen(data)  # MODULO: ENLACE
                # TODO pasar el result al modulo logging para general el log
            elif (opcion == 7):
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
            opcion = self.validador.obtener_int(
                'Ingrese la opción: ', minValor=1, maxValor=4)
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
