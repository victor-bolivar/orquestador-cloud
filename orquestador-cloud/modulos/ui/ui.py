#!/usr/bin/env python3

from ..logging.Exceptions import InputException
from ..validador.validador import Validador
from ..enlace.enlace import Enlace
from ..logging.Logging import Logging

import sys
import json
import webbrowser
from prettytable import PrettyTable


class UI:
    def __init__(self):
        self.enlace = Enlace()
        self.validador = Validador()
        self.logging = Logging()

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
                # 1. Se listan las topologias para que el usuario ingrese el ID
                self.enlace.listar_topologias()
                print()  # print new line
                # 2. El usuario ingresa el ID de la topologia
                topology_id = self.validador.obtener_int(
                    'Ingrese el ID de la Topología: ')
                # 3. Sise ingresa una opcion valida, se obtiene el json
                if(topology_id):
                    self.enlace.topologia_json(topology_id)
                else:
                    print('[x] Ingrese una opción válida')

            elif (opcion == 3):
                # 1. Se listan las topologias para que el usuario ingrese el ID
                self.enlace.listar_topologias()
                print()  # print new line
                # 2. El usuario ingresa el ID de la topologia
                topology_id = self.validador.obtener_int(
                    'Ingrese el ID de la Topología: ')
                if(topology_id):
                    topologia_json_visualizador = self.enlace.topologia_visualizador(
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

                else:
                    print('[x] Ingrese una opción válida')

            elif (opcion == 4):
                print()
                self.enlace.listar_imagenes()

            elif (opcion == 5):
                pass
        else:
            # Si no se especifico una opcion valida, se procede con el bucle
            print('[x] Ingrese una opción válida')

    # Opcion 2

    def opcion_2(self):
        try:
            # 1. se obtiene la informacion de los workers e imagenes que necesita el modulo validador
            workers_info = self.enlace.workers_info()
            imagenes = self.enlace.obtener_imagenes()
            # 2. se pide la informacion de la topologia a crear al usuario
            nueva_topologia = self.validador.nueva_topologia(
                workers_info, imagenes)

            # 2. se pide al usuario que confirme la informacion ingresada 
            print('A continuacion se muestra la configuracion ingresada: \n')
            topology_json = json.dumps(nueva_topologia, indent=4)
            topology_json = '                '+topology_json
            topology_json = topology_json.replace("\n", "\n                ")
            print(topology_json)
            opcion = self.validador.obtener_int(
                '\n¿Desea proceder con la creacion de la topologia? (1. Si | 2. No): ')
            print()
            if (opcion == 1):
                # 3. se verifica que existen los recursos suficientes y se separan los recursos en la DB
                [recursos_suficientes, result] = self.enlace.separar_recursos_topologia(nueva_topologia)
                self.logging.log(result)
                
                if recursos_suficientes:
                    # 4. ya que ya se separaron los recursos en la db, se procede a crear la topologia
                    result = self.enlace.crear_topologia(nueva_topologia)
                    self.logging.log(result)
                else:
                    print('[-] No se realizo la creacion de la topologia debido a recursos insuficientes en el slice')
                    print('\nSe recomienda aumentar la capacidad del slice o dismuir la capacidad de las maquinas a desplegar')
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
                # 1. se listan las topologias
                self.enlace.listar_topologias()
                # 2. el usuario ingresa el ID de la topologia a eliminar
                id_topologia = self.validador.obtener_int('\nIngrese el ID: ')
                # 3. se elima la topologia
                result = self.enlace.eliminar_topologia(id_topologia)
                self.logging.log(result)

            elif (opcion == 2):
                # 1. se listan las topologias
                self.enlace.listar_topologias()

                # 2. se obtiene la tabla de imagenes de la db que necesita el modulo validador
                tabla_imagenes = self.enlace.obtener_imagenes()
                # 3. se obtiene la data del usuario para la creacion de la VM
                data = self.validador.agregar_nodo(tabla_imagenes)
                
                # 4. se pide al usuario confirmar la informacion ingresada
                print('A continuacion se muestra la configuracion ingresada: \n')
                data_json = json.dumps(data, indent=4)
                data_json = '                '+data_json
                data_json = data_json.replace("\n", "\n                ")
                print(data_json)
                opcion = self.validador.obtener_int(
                    '\n¿Desea proceder con la creacion del nodo? (1. Si | 2. No): ')
                print()
                if (opcion == 1):

                    # 3. se verifica que existen los recursos suficientes y se separan los recursos en la DB
                    [recursos_suficientes, result] = self.enlace.separar_recursos_nodo(data)
                    self.logging.log(result)
                    
                    if recursos_suficientes:
                        # 4. ya que ya se separaron los recursos en la db, se procede a crear el nodo
                        result = self.enlace.agregar_nodo(data)
                        self.logging.log(result)
                    else:
                        print('[-] No se realizo la creacion del nodo debido a recursos insuficientes en el slice')
                        print('\nSe recomienda aumentar la capacidad del slice o dismuir la capacidad del nodo a desplegar')
                    
                elif (opcion == 2):
                    print('[-] No se realizo la creacion del nodo')
                else:
                    print('[x] Ingrese una opcion valida')

            elif (opcion == 3):
                # 1. se listan las topologias y se pide el ID
                self.enlace.listar_topologias()
                id_topologia = self.validador.obtener_int(
                    '\nIngrese el ID de la topologia: ')
                # 2. se listan los nodos y se pide el ID
                self.enlace.listar_nodos(id_topologia)
                id_nodo = self.validador.obtener_int(
                    '\nIngrese el ID del nodo: ')
                # 3. se elimnina el nodo
                result = self.enlace.eliminar_nodo(id_topologia, id_nodo)
                self.logging.log(result)

            elif (opcion == 4):
                # 1. se listan las topologias y se pide el ID
                self.enlace.listar_topologias()
                id_topologia = self.validador.obtener_int(
                    '\nIngrese el ID de la topologia: ')
                print()

                # 2. TODO listar los workers actuales en la topologia
                
                # 3. se obtiene de la db un resumen de las metricas de los workers 
                workers_info = self.enlace.workers_info()
                # 4. se pide al usuario que workers desea añadir
                data = self.validador.aumentar_slice(workers_info)
                # 5. se añade los workers al slice
                result = self.enlace.aumentar_slice(data)
                self.logging.log(result)

            elif (opcion == 5):
                # 1. e listan las topologias y se pide el ID
                self.enlace.listar_topologias()
                id_topologia = self.validador.obtener_int(
                    '\nIngrese el ID de la topologia: ')
                
                # 2. se listan los nodos y se pide el ID 
                self.enlace.listar_nodos(id_topologia)
                id_nodo = self.validador.obtener_int(
                    '\nIngrese el ID del nodo: ')

                # 3. se da conectividad a internet al nodo especificado
                result = self.enlace.conectar_nodo_internet(id_nodo)
                self.logging.log(result)

            elif (opcion == 6):
                # 1. se obtien la informacion de la imagen a importar
                data = self.validador.importar_imagen()  
                # 2. se importa la imagen
                result = self.enlace.importar_imagen(data)
                # 3. se loggea el resultado
                self.logging.log(result)
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
