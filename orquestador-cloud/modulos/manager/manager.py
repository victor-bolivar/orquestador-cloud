#!/usr/bin/env python3

from ..logging.Exceptions import InputException
from ..validador.validador import Validador
from ..driver.driver import Driver
from ..logging.Logging import Logging

import sys
import json
import webbrowser

class Manager:
    def __init__(self):
        self.driver = Driver()
        self.validador = Validador()
        self.logging = Logging()

        data_lc = {
            "nombre": "prueba1",
            "tipo": "lineal",
            "infraestructura": {
                "infraestructura": "Linux Cluster",
                "az": [
                    "1",
                    "2"
                ]
            },
            "vms": [
                {
                    "nombre": 'vm1',
                    "n_vcpus": 1,
                    "memoria": 1,
                    "filesystem": {
                        "filesystem": "CopyOnWrite",
                        "size": 1
                    },
                    "imagen_id": 19,
                    "internet": True
                },
                {
                    "nombre": 'vm2',
                    "n_vcpus": 1,
                    "memoria": 1,
                    "filesystem": {
                        "filesystem": "CopyOnWrite",
                        "size": 1
                    },
                    "imagen_id": 19,
                    "internet": True
                },
                {
                    "nombre": 'vm3',
                    "n_vcpus": 1,
                    "memoria": 1,
                    "filesystem": {
                        "filesystem": "CopyOnWrite",
                        "size": 1
                    },
                    "imagen_id": 19,
                    "internet": False
                }
            ]
        }

        data_op = {
                    "nombre": "aaa",
                    "tipo": "lineal",
                    "infraestructura": {
                        "infraestructura": "OpenStack",
                        "az": [
                            "1001",
                            "1002"
                        ]
                    },
                    "vms": [
                        {
                            "nombre": 'vm1',
                            "n_vcpus": 1,
                            "memoria": 1,
                            "filesystem": {
                                "filesystem": "CopyOnWrite",
                                "size": 10
                            },
                            "imagen_id": 19,
                            "internet": True
                        },
                        {
                            "nombre": 'vm2',
                            "n_vcpus": 1,
                            "memoria": 1,
                            "filesystem": {
                                "filesystem": "CopyOnWrite",
                                "size": 10
                            },
                            "imagen_id": 19,
                            "internet": True
                        },
                        {
                            "nombre": 'vm3',
                            "n_vcpus": 1,
                            "memoria": 1,
                            "filesystem": {
                                "filesystem": "CopyOnWrite",
                                "size": 10
                            },
                            "imagen_id": 19,
                            "internet": False
                        }
                    ]
                }
        #print(self.driver.recursos_suficientes_topologia(data))
        #print(self.driver.crear_topologia(data_lc, debug=True))
        data_nodo = {
                    'id_topologia': "54",
                    "nombre": 'vm1',
                    "n_vcpus": 1,
                    "memoria": 1,
                    "filesystem": {
                        "filesystem": "CopyOnWrite",
                        "size": 1
                    },
                    "imagen_id": 19,
                    "internet": True
                }
        print(self.driver.recursos_suficientes_nodo(data_nodo))

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
                self.driver.listar_topologias()

            elif (opcion == 2):
                # 1. Se listan las topologias para que el usuario ingrese el ID
                self.driver.listar_topologias()
                print()  # print new line
                # 2. El usuario ingresa el ID de la topologia
                topology_id = self.validador.obtener_int(
                    'Ingrese el ID de la Topología: ')
                # 3. Si se ingresa una opcion valida, se obtiene el json
                if(topology_id):
                    self.driver.topologia_json(topology_id)
                else:
                    raise InputException()

            elif (opcion == 3):
                # 1. Se listan las topologias para que el usuario ingrese el ID
                self.driver.listar_topologias()
                print()  # print new line
                # 2. El usuario ingresa el ID de la topologia
                topology_id = self.validador.obtener_int(
                    'Ingrese el ID de la Topología: ')
                if(topology_id):
                    topologia_json_visualizador = self.driver.topologia_visualizador(
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
                    raise InputException()

            elif (opcion == 4):
                print()
                self.driver.listar_imagenes()

            elif (opcion == 5):
                pass
        else:
            # Si no se especifico una opcion valida, se procede con el bucle
            raise InputException()

    # Opcion 2

    def opcion_2(self):
        # 1. se obtiene la informacion de los workers e imagenes que necesita el modulo validador
        workers_info = self.driver.workers_info()
        imagenes = self.driver.obtener_imagenes()
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
            recursos_suficientes = self.driver.recursos_suficientes_topologia(nueva_topologia)
                
            if recursos_suficientes:
                # 4. se procede a crear la topologia
                result = self.driver.crear_topologia(nueva_topologia)
                self.logging.log(result)
            else:
                print('[-] No se realizo la creacion de la topologia debido a recursos insuficientes en el slice')
                print('\nSe recomienda aumentar la capacidad del slice o dismuir la capacidad de las maquinas a desplegar')
        elif (opcion == 2):
            print('[-] No se realizo la creacion de la topologia')
        else:
            raise InputException()

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
                3.6 Importar imagen 
                3.7 Regresar
            ''')
        opcion = self.validador.obtener_int(
            'Ingrese la opción: ', minValor=1, maxValor=7)
        if(opcion):
            if (opcion == 1):
                # 1. se listan las topologias
                self.driver.listar_topologias()
                # 2. el usuario ingresa el ID de la topologia a eliminar
                id_topologia = self.validador.obtener_int('\nIngrese el ID: ')
                if(id_topologia):
                    # 3. se elima la topologia
                    result = self.driver.eliminar_topologia(id_topologia)
                    self.logging.log(result)
                else:
                    raise InputException()

            elif (opcion == 2):
                # 1. se listan las topologias
                self.driver.listar_topologias()

                # 2. se obtiene la tabla de imagenes de la db que necesita el modulo validador
                tabla_imagenes = self.driver.obtener_imagenes()
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
                    recursos_suficientes = self.driver.recursos_suficientes_nodo(data)
                    
                    if recursos_suficientes:
                        # 4. ya que ya se valida que hay los recursos en la db, se procede a crear el nodo
                        result = self.driver.agregar_nodo(data)
                        self.logging.log(result)
                    else:
                        print('[-] No se realizo la creacion del nodo debido a recursos insuficientes en el slice')
                        print('\nSe recomienda aumentar la capacidad del slice o dismuir la capacidad del nodo a desplegar')
                    
                elif (opcion == 2):
                    print('[-] No se realizo la creacion del nodo')
                else:
                    raise InputException()

            elif (opcion == 3):
                # 1. se listan las topologias y se pide el ID
                self.driver.listar_topologias()
                id_topologia = self.validador.obtener_int(
                    '\nIngrese el ID de la topologia: ')
                if(id_topologia):
                    # 2. se listan los nodos y se pide el ID
                    self.driver.listar_nodos(id_topologia)
                    id_nodo = self.validador.obtener_int(
                        '\nIngrese el ID del nodo: ')
                    if(id_nodo):
                        # 3. se elimnina el nodo
                        result = self.driver.eliminar_nodo(id_topologia, id_nodo)
                        self.logging.log(result)
                    else:
                        raise InputException()
                else:
                    raise InputException()

            elif (opcion == 4):
                # 1. se listan las topologias y se pide el ID
                self.driver.listar_topologias()
                id_topologia = self.validador.obtener_int(
                    '\nIngrese el ID de la topologia: ')
                if(id_topologia):
                    print()
                    # 2. se listan los workers actuales en la topologia
                    self.driver.listar_workers_actuales(id_topologia)
                    
                    # 3. se obtiene de la db un resumen de las metricas de los workers y los IDs de workers para esa infraestructura
                    workers_info = self.driver.workers_info_slice(id_topologia)
                    workers_ids = ['1001', '1002', '1003'] # TODO
                    # 4. se pide al usuario que workers desea añadir
                    data = self.validador.aumentar_slice(workers_info, workers_ids)
                    # 5. se añade los workers al slice
                    result = self.driver.aumentar_slice(data)
                    self.logging.log(result)
                else:
                    raise InputException()

            elif (opcion == 5):
                # 1. se listan las topologias y se pide el ID
                self.driver.listar_topologias()
                id_topologia = self.validador.obtener_int(
                    '\nIngrese el ID de la topologia: ')
                if(id_topologia):
                    # 2. se listan los nodos y se pide el ID 
                    self.driver.listar_nodos(id_topologia)
                    id_nodo = self.validador.obtener_int(
                        '\nIngrese el ID del nodo: ')

                    if(id_nodo):
                        # 3. se da conectividad a internet al nodo especificado
                        result = self.driver.conectar_nodo_internet(id_nodo)
                        self.logging.log(result)
                    else:
                        raise InputException()
                else:
                    raise InputException()

            elif (opcion == 6):
                # 1. se obtien la informacion de la imagen a importar
                data = self.validador.importar_imagen()  
                # 2. se importa la imagen
                result = self.driver.importar_imagen(data)
                # 3. se loggea el resultado
                self.logging.log(result)
            elif (opcion == 7):
                pass
        else:
            # Si no se especifico una opcion valida, se procede con el bucle
            raise InputException()

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
                try: 
                    if (opcion == 1):
                        self.opcion_1()
                    elif (opcion == 2):
                        self.opcion_2()
                    elif (opcion == 3):
                        self.opcion_3()
                    elif (opcion == 4):
                        sys.exit(0)
                except InputException as inputException:
                    print()
                    print(inputException)
            else:
                print('\n[x] Ingrese una opcion valida')
                # Si no se especifico una opcion valida, se procede con el bucle
                continue
