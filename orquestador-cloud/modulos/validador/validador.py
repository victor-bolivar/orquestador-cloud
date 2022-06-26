#!/usr/bin/env python3

from ..logging.Exceptions import InputException

from typing import Optional
from prettytable import PrettyTable


class Validador():
    def __init__(self) -> None:
        pass

    def obtener_int(self, label, maxValor: Optional[int] = None, minValor: Optional[int] = None, valoresValidos: Optional[list] = None) -> int or False:
        '''
            label: texto a mostrar en la linea de comandos al pedir input

            Devuelve el valor 'integer' si la validacion es satisfactoria, sino se devuelve el booleano 'False'
        '''

        variable = input(label)
        if (variable.isdigit()):
            # si es que es un digito
            integer = int(variable)
            # validaciones
            if (maxValor and minValor):
                # si es que se especifico un rango, se valida
                return integer if (minValor <= integer <= maxValor) else False
            elif (valoresValidos):
                # si se especifico un rango de valores
                return integer if (integer in valoresValidos) else False
            else:
                # si no se especifico un rango, se devuelve el entero de frente
                return integer
        else:
            return False

    # Opcion 2: Crear Topologia

    def nueva_topologia(self, workers_info: dict, tabla_imagenes: str) -> dict:
        '''
        input
        ---
            workers_info:   se recibe un diccionario con la informacion de los workers dentro de cada infraestructura
                            con el fin de que el usuario defina su AZ.

                            este diccionario se pasaria a la funcion validador.obtener_infraestructura()

                            {
                                'openstack': tabla_a_imprimir(str),
                                'linux_cluster': tabla_a_imprimir(str),
                            }
            tabla_imagenes: tabla conteniendo la informacion de las imagenes disponibles parala creacion de VMs

        outputs
        ---
            topologia: diccionario con la informacion de la topologia a crear

                            {
                                'nombre': str,
                                'tipo': str, 
                                'infraestructura': dict,
                                'vms': list
                            }

                        donde los valores posibles son:
                            tipo: ['lineal', 'malla','arbol', 'anillo', 'bus']
                            infraestructura: 
                                    Si escoge 'OpenStack'
                                    {
                                        'infraestructura': 'OpenStack'
                                        'az': [ 1, 2, 3]
                                    }
                                    Si escoge 'Linux Cluster' 
                                    {
                                        'infraestructura': 'Linux Cluster'
                                        'az': [ 1, 2, 3]
                                    }

            por ejemplo:

                {
                    "nombre": "topologia1",
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
                            "n_vcpus": 1,
                            "memoria": 2,
                            "filesystem": {
                                "filesystem": "CopyOnWrite"
                            },
                            "imagen_id": 1,
                            "internet": true,
                        },
                        {
                            "n_vcpus": 4,
                            "memoria": 4,
                            "filesystem": {
                                "filesystem": "Raw",
                                "size": 10
                            },
                            "imagen_id": 3,
                            "internet": true,
                        },
                        {
                            "n_vcpus": 8,
                            "memoria": 2,
                            "filesystem": {
                                "filesystem": "Raw",
                                "size": 50
                            },
                            "imagen_id": 3,
                            "internet": false,
                        }
                    ]
                }

        '''
        nombre = input('\nIngrese el nombre de la topologia: ')
        tipo = self.obtener_tipo_topologia()
        infraestructura = self.obtener_infraestructura(workers_info)
        # datos de las 3 VMs a crear (numero predefinido para las topologias predefinidas)
        print()
        print('A continuacion se le pedira la informacion de las 3 VMs a crear para la topologia predefinida')
        print('Por favor, tenga en cuenta la tabla de recursos disponibles para su AZ mostrada previamente\n')
        vms = []
        for i in range(1, 4):
            print('            ------ Maquina virtual #'+str(i)+' ------\n')
            n_vcpus = self.obtener_numero_vcpus()
            memoria = self.obtener_memoria()
            filesystem = self.obtener_fs()
            imagen_id = self.obtener_imagen(tabla_imagenes)
            internet = self.conectar_internet()
            print()
            vms.append({
                'n_vcpus': n_vcpus,
                'memoria': memoria,
                'filesystem': filesystem,
                'imagen_id': imagen_id,
                'internet': internet
            })

        return {
            'nombre': nombre,
            'tipo': tipo,
            'infraestructura': infraestructura,
            'vms': vms
        }

    def obtener_tipo_topologia(self) -> str:
        topologias_validas = ['(1)lineal', '(2)malla',
                              '(3)arbol', '(4)anillo', '(5)bus']
        variable = self.obtener_int(
            'Ingrese el tipo de topologia '+str(topologias_validas)+': ', minValor=1, maxValor=5)
        if(variable == 1):
            return 'lineal'
        elif(variable == 2):
            return 'malla'
        elif(variable == 3):
            return 'arbol'
        elif(variable == 4):
            return 'anillo'
        elif(variable == 5):
            return 'bus'
        else:
            raise InputException()

    def obtener_infraestructura(self, workers_info) -> dict:
        '''
            inputs
            ---
            workers_info:   se recibe un diccionario con la informacion de los workers dentro de cada infraestructura
                            con el fin de que el usuario defina su AZ

                            {
                                'openstack': tabla_a_imprimir,
                                'linux_cluster': tabla_a_imprimir,
                            }

            outputs
            ---
            Se devuelve un diccionario con la informacion del tipo de infraestructura y una lista
            con los ID de los workers que el usuario escogio para su AZ

            Si escoge 'OpenStack'

            {
                'infraestructura': 'OpenStack'
                'az': [ 1, 2, 3]
            }

            Si escoge 'Linux Cluster' 
            {
                'infraestructura': 'Linux Cluster'
                'az': [ 1, 2, 3]
            }
        '''

        infraestructuras_validas = ['(1)Linux Cluster', '(2)OpenStack']
        input_tipo_infraestructura = self.obtener_int(
            'Ingrese el tipo de infraestructura '+str(infraestructuras_validas)+': ', valoresValidos=[1, 2])
        print()
        if (input_tipo_infraestructura == 2):
            # caso: openstack

            print(workers_info['openstack'])
            print()
            print(
                'Elija el(los) worker(s) donde desea desplegar su zona de disponibilidad ')
            input_az = input(
                'Ingrese los IDs sin espacio y separado por comas (ex: 1001,1002,1003): ')
            workers_validos = ['1001', '1002', '1003']
            input_az = input_az.split(',')
            if(set(input_az).issubset(workers_validos)):
                # se devuelve la lista de compute-nodes
                # se pasa antes por set() para eliminar duplicados en la lista
                return {
                    'infraestructura': 'OpenStack',
                    'az': input_az
                }
            else:
                raise InputException()
        elif (input_tipo_infraestructura == 1):
            # caso: linux cluster

            print(workers_info['linux_cluster'])
            print()
            print(
                'Elija el(los) worker(s) donde desea desplegar su zona de disponibilidad ')
            input_az = input(
                'Ingrese los IDs sin espacio y separado por comas (ex: 1,2,3): ')
            workers_validos = ['1', '2', '3']
            input_az = input_az.split(',')
            if(set(input_az).issubset(workers_validos)):
                # se devuelve la lista de compute-nodes
                # se pasa antes por set() para eliminar duplicados en la lista
                return {
                    'infraestructura': 'Linux Cluster',
                    'az': input_az
                }
            else:
                raise InputException()
        else:
            raise InputException()

    def conectar_internet(self) -> int:
        opcion = self.obtener_int(
            '¿Desea que el nodo tenga conexión a Internet? (1. Si | 2. No): ', minValor=1, maxValor=2)
        if (opcion == 1):
            return True
        elif (opcion == 2):
            return False
        else:
            raise InputException()

    def obtener_numero_vcpus(self) -> int:
        valores_validos = [1, 2, 4, 8]

        # se imprime la tabla
        t = PrettyTable(valores_validos)
        t.padding_width = 1
        t.title = 'vCPUs'
        # modificacion para que no se vea la ultima linea
        t = str(t)[:str(t).rfind('\n')]
        # para añadir identacion a la tabla
        t = '                '+t
        t = t.replace("\n", "\n                ")
        print(t)
        print()
        n_vcpus = self.obtener_int(
            'Elija el número de vCPUs: ', valoresValidos=valores_validos)
        print()
        if n_vcpus:
            return n_vcpus
        else:
            raise InputException()

    def obtener_memoria(self) -> int:
        valores_validos = [1, 2, 4, 8]

        # se imprime la tabla
        t = PrettyTable(valores_validos)
        t.padding_width = 1
        t.title = 'Memoria (GB)'
        # modificacion para que no se vea la ultima linea
        t = str(t)[:str(t).rfind('\n')]
        # para añadir identacion a la tabla
        t = '                '+t
        t = t.replace("\n", "\n                ")
        print(t)
        print()
        input_memoria = self.obtener_int(
            'Elija el tamaño de la memoria: ', valoresValidos=valores_validos)
        print()
        if input_memoria:
            return input_memoria
        else:
            raise InputException()

    def obtener_fs(self) -> int:
        '''
            output
            ---
            se devuelve un diccionario con la data correspondiente.

            opcion1: CopyOnWrite FileSystem
                {
                    'filesystem': 'CopyOnWrite'
                }
            opcion2: Raw FileSystem
                {
                    'filesystem': 'Raw',
                    'size': tamaño
                }

        '''
        print('A continuación definirá la cantidad de almacenamiento y tipo de almacenamiento en base a sus requerimientos')
        print('     1. CopyOnWrite FileSystem: si no piensa instalar muchos paquetes adicionales (como un switch o router)')
        print('     2. Raw FileSystem: Si piensa descargar muchos archivos o paquetes (como una base de datos)')
        opcion = self.obtener_int(
            'Seleccionar la opción adecuada para su escenario: ', minValor=1, maxValor=2)
        print()
        if (opcion):
            if(opcion == 1):
                return {
                    'filesystem': 'CopyOnWrite'
                }
            elif(opcion == 2):
                tamaño = self.obtener_int(
                    'Ingresar la cantidad de almacenamiento (Mínimo:10 GB | Máximo: 80 GB): ', minValor=10, maxValor=80)
                print()
                if (tamaño):
                    return {
                        'filesystem': 'Raw',
                        'size': tamaño
                    }
                else: 
                    raise InputException()
        else:
            raise InputException()

    def obtener_imagen(self, tabla_imagenes) -> int:
        '''
            tabla_imagenes: tabla que contiene las imagenes disponibles en el sistema
        '''
        print(tabla_imagenes)
        print()
        imagen_id = self.obtener_int('Ingrese el ID: ')
        print()
        if(imagen_id):
            return imagen_id
        else:
            raise InputException()

    # Opcion 3: Editar

    def importar_imagen(self) -> dict:
        '''
            Dependiendo de la opcion se retorna:

            opcion 1:
            ---
                {   'opcion':opcion,
                    'nombre':nombre,
                    'categoria':categoria,
                    'ruta':ruta  }

            opcion 2:
            ---
                {   'opcion':opcion,
                    'nombre':nombre,
                    'categoria':categoria,
                    'url':url  }
        '''
        print('''
            1. Seleccionar un archivo local
            2. Ingresar un URL para ser descargado por el controlador
        ''')
        opcion = self.obtener_int('Ingrese la opcion: ', valoresValidos=[1, 2])
        nombre = input('\nIngrese un nombre para la imagen: ')
        categorias_validas = ['server', 'security', 'networking']
        categoria = input('Ingrese el nombre de la categoria ' +
                          str(categorias_validas)+': ')

        if (categoria in categorias_validas):
            if (opcion == 1):
                ruta = input('Ingrese la ruta del archivo: ')
                return {'opcion': opcion,
                        'nombre': nombre,
                        'categoria': categoria,
                        'ruta': ruta}
            elif (opcion == 2):
                url = input('Ingrese la url de la imagen: ')
                return {'opcion': opcion,
                        'nombre': nombre,
                        'categoria': categoria,
                        'url': url}
            else:
                raise InputException()
        else:
            raise InputException()

    def agregar_nodo(self, tabla_imagenes:str) -> dict:
        id_topologia = self.obtener_int('\nIngrese el ID: ')
        print()
        n_vcpus = self.obtener_numero_vcpus()
        memoria = self.obtener_memoria()
        filesystem = self.obtener_fs()
        imagen_id = self.obtener_imagen(tabla_imagenes)
        internet = self.conectar_internet()
        return {
            'id_topologia': id_topologia,
            'n_vcpus': n_vcpus,
            'memoria': memoria,
            'filesystem': filesystem,
            'imagen_id': imagen_id,
            'internet': internet
        }

    def aumentar_slice(self, workers_info:str, workers_ids:list) -> list:
        '''
            input 
            ---
            workers_info(str): tabla a imprimir con la informacion de los workers 
                                en la infraestructura del slice

            output
            ---
            input_az: lista con los IDs de los workers que se van a añadir al slice
        '''
        print(workers_info)
        print('\nElija el(los) worker(s) con los cuales desea aumentar su zona de disponibilidad ')
        input_az = input(
            'Ingrese los IDs sin espacio y separado por comas (ex: 1001,1002,1003): ')
        input_az = input_az.split(',')
        if(set(input_az).issubset(workers_ids)):
            # se devuelve la lista de compute-nodes
            # se pasa antes por set() para eliminar duplicados en la lista
            return input_az
        else:
            raise InputException()

class ValidadorTest():
    '''
        Clase paralela a Validador pero con la modificacion de que se le pasan los inputs como
        argumentos (en lugar de ser ingresados por el usuario mediante el CLI) con el fin
        de verificar que se devuelva la informacion requerida en el formato adecuado segun corresponda.
    '''
    def __init__(self) -> None:
        pass

    def obtener_int(self, label, valueTest, maxValor: Optional[int] = None, minValor: Optional[int] = None, valoresValidos: Optional[list] = None) -> int or False:
        '''
            label: texto a mostrar en la linea de comandos al pedir input

            Devuelve el valor 'integer' si la validacion es satisfactoria, sino se devuelve el booleano 'False'
        '''

        # variable = input(label)
        variable = valueTest

        if (variable.isdigit()):
            # si es que es un digito
            integer = int(variable)
            # validaciones
            if (maxValor and minValor):
                # si es que se especifico un rango, se valida
                return integer if (minValor <= integer <= maxValor) else False
            elif (valoresValidos):
                # si se especifico un rango de valores
                return integer if (integer in valoresValidos) else False
            else:
                # si no se especifico un rango, se devuelve el entero de frente
                return integer
        else:
            return False

    # Opcion 2: Crear Topologia

    def nueva_topologia(self, workers_info: dict, tabla_imagenes: str, valuesTest:dict) -> dict:
        '''
        input
        ---
            workers_info:   se recibe un diccionario con la informacion de los workers dentro de cada infraestructura
                            con el fin de que el usuario defina su AZ.

                            este diccionario se pasaria a la funcion validador.obtener_infraestructura()

                            {
                                'openstack': tabla_a_imprimir(str),
                                'linux_cluster': tabla_a_imprimir(str),
                            }
            tabla_imagenes: tabla conteniendo la informacion de las imagenes disponibles parala creacion de VMs

        outputs
        ---
            topologia: diccionario con la informacion de la topologia a crear

                            {
                                'nombre': str,
                                'tipo': str, 
                                'infraestructura': dict,
                                'vms': list
                            }

                        donde los valores posibles son:
                            tipo: ['lineal', 'malla','arbol', 'anillo', 'bus']
                            infraestructura: 
                                    Si escoge 'OpenStack'
                                    {
                                        'infraestructura': 'OpenStack'
                                        'az': [ 1, 2, 3]
                                    }
                                    Si escoge 'Linux Cluster' 
                                    {
                                        'infraestructura': 'Linux Cluster'
                                        'az': [ 1, 2, 3]
                                    }

            por ejemplo:

                {
                    "nombre": "topologia1",
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
                            "n_vcpus": 1,
                            "memoria": 2,
                            "filesystem": {
                                "filesystem": "CopyOnWrite"
                            },
                            "imagen_id": 1,
                            "internet": true,
                        },
                        {
                            "n_vcpus": 4,
                            "memoria": 4,
                            "filesystem": {
                                "filesystem": "Raw",
                                "size": 10
                            },
                            "imagen_id": 3,
                            "internet": true,
                        },
                        {
                            "n_vcpus": 8,
                            "memoria": 2,
                            "filesystem": {
                                "filesystem": "Raw",
                                "size": 50
                            },
                            "imagen_id": 3,
                            "internet": false,
                        }
                    ]
                }

        '''
        #nombre = input('\nIngrese el nombre de la topologia: ')
        nombre = valuesTest['nombre']
        #tipo = self.obtener_tipo_topologia()
        tipo = valuesTest['tipo']
        #infraestructura = self.obtener_infraestructura(workers_info)
        infraestructura = valuesTest['infraestructura']
        # datos de las 3 VMs a crear (numero predefinido para las topologias predefinidas)
        #print()
        #print('A continuacion se le pedira la informacion de las 3 VMs a crear para la topologia predefinida')
        #print('Por favor, tenga en cuenta la tabla de recursos disponibles para su AZ mostrada previamente\n')
        vms = []
        for i in range(1, 4):
            #print('            ------ Maquina virtual #'+str(i)+' ------\n')
            #n_vcpus = self.obtener_numero_vcpus()
            n_vcpus = valuesTest['vms'][i-1]['n_vcpus']
            #memoria = self.obtener_memoria()
            memoria = valuesTest['vms'][i-1]['memoria']
            #filesystem = self.obtener_fs()
            filesystem = valuesTest['vms'][i-1]['filesystem']
            #imagen_id = self.obtener_imagen(tabla_imagenes)
            imagen_id = valuesTest['vms'][i-1]['imagen_id']
            #internet = self.conectar_internet()
            internet = valuesTest['vms'][i-1]['internet']
            #print()
            vms.append({
                'n_vcpus': n_vcpus,
                'memoria': memoria,
                'filesystem': filesystem,
                'imagen_id': imagen_id,
                'internet': internet
            })

        return {
            'nombre': nombre,
            'tipo': tipo,
            'infraestructura': infraestructura,
            'vms': vms
        }

    def obtener_tipo_topologia(self, valueTest:int) -> str:
        topologias_validas = ['(1)lineal', '(2)malla',
                              '(3)arbol', '(4)anillo', '(5)bus']
        #variable = self.obtener_int('Ingrese el tipo de topologia '+str(topologias_validas)+': ', minValor=1, maxValor=5)
        variable = valueTest
        
        if(variable == 1):
            return 'lineal'
        elif(variable == 2):
            return 'malla'
        elif(variable == 3):
            return 'arbol'
        elif(variable == 4):
            return 'anillo'
        elif(variable == 5):
            return 'bus'
        else:
            raise InputException()

    def obtener_infraestructura(self, workers_info, testInfraestructura:int, testAz:str) -> dict:
        '''
            inputs
            ---
            workers_info:   se recibe un diccionario con la informacion de los workers dentro de cada infraestructura
                            con el fin de que el usuario defina su AZ

                            {
                                'openstack': tabla_a_imprimir,
                                'linux_cluster': tabla_a_imprimir,
                            }

            outputs
            ---
            Se devuelve un diccionario con la informacion del tipo de infraestructura y una lista
            con los ID de los workers que el usuario escogio para su AZ

            Si escoge 'OpenStack'

            {
                'infraestructura': 'OpenStack'
                'az': [ 1, 2, 3]
            }

            Si escoge 'Linux Cluster' 
            {
                'infraestructura': 'Linux Cluster'
                'az': [ 1, 2, 3]
            }
        '''

        infraestructuras_validas = ['(1)Linux Cluster', '(2)OpenStack']
        # input_tipo_infraestructura = self.obtener_int('Ingrese el tipo de infraestructura '+str(infraestructuras_validas)+': ', valoresValidos=[1, 2])
        input_tipo_infraestructura = testInfraestructura
        #print()
        if (input_tipo_infraestructura == 2):
            # caso: openstack

            #print(workers_info['openstack'])
            #print()
            #print( 'Elija el(los) worker(s) donde desea desplegar su zona de disponibilidad ')
            #input_az = input( 'Ingrese los IDs sin espacio y separado por comas (ex: 1001,1002,1003): ')
            input_az = testAz
            workers_validos = ['1001', '1002', '1003']
            input_az = input_az.split(',')
            if(set(input_az).issubset(workers_validos)):
                # se devuelve la lista de compute-nodes
                # se pasa antes por set() para eliminar duplicados en la lista
                return {
                    'infraestructura': 'OpenStack',
                    'az': input_az
                }
            else:
                raise InputException()
        elif (input_tipo_infraestructura == 1):
            # caso: linux cluster

            #print(workers_info['linux_cluster'])
            #print()
            #print( 'Elija el(los) worker(s) donde desea desplegar su zona de disponibilidad ')
            #input_az = input('Ingrese los IDs sin espacio y separado por comas (ex: 1,2,3): ')
            input_az = testAz
            workers_validos = ['1', '2', '3']
            input_az = input_az.split(',')
            if(set(input_az).issubset(workers_validos)):
                # se devuelve la lista de compute-nodes
                # se pasa antes por set() para eliminar duplicados en la lista
                return {
                    'infraestructura': 'Linux Cluster',
                    'az': input_az
                }
            else:
                raise InputException()
        else:
            raise InputException()

    def conectar_internet(self, inputTest:int) -> int:
        #opcion = self.obtener_int('¿Desea que el nodo tenga conexión a Internet? (1. Si | 2. No): ', minValor=1, maxValor=2)
        opcion = inputTest
        if (opcion == 1):
            return True
        elif (opcion == 2):
            return False
        else:
            raise InputException()

    def obtener_numero_vcpus(self, inputTest:int) -> int:
        valores_validos = [1, 2, 4, 8]

        # se imprime la tabla
        t = PrettyTable(valores_validos)
        t.padding_width = 1
        t.title = 'vCPUs'
        # modificacion para que no se vea la ultima linea
        t = str(t)[:str(t).rfind('\n')]
        # para añadir identacion a la tabla
        t = '                '+t
        t = t.replace("\n", "\n                ")
        #print(t)
        #print()
        #n_vcpus = self.obtener_int('Elija el número de vCPUs: ', valoresValidos=valores_validos)
        n_vcpus = inputTest
        #print()
        if n_vcpus:
            return n_vcpus
        else:
            raise InputException()

    def obtener_memoria(self, inputTest:int) -> int:
        valores_validos = [1, 2, 4, 8]

        # se imprime la tabla
        t = PrettyTable(valores_validos)
        t.padding_width = 1
        t.title = 'Memoria (GB)'
        # modificacion para que no se vea la ultima linea
        t = str(t)[:str(t).rfind('\n')]
        # para añadir identacion a la tabla
        t = '                '+t
        t = t.replace("\n", "\n                ")
        #print(t)
        #print()
        #input_memoria = self.obtener_int('Elija el tamaño de la memoria: ', valoresValidos=valores_validos)
        input_memoria = inputTest
        #print()
        if input_memoria:
            return input_memoria
        else:
            raise InputException()

    def obtener_fs(self, fsTest:int, sizeTest:int=None) -> int:
        '''
            output
            ---
            se devuelve un diccionario con la data correspondiente.

            opcion1: CopyOnWrite FileSystem
                {
                    'filesystem': 'CopyOnWrite'
                }
            opcion2: Raw FileSystem
                {
                    'filesystem': 'Raw',
                    'size': tamaño
                }

        '''
        #print('A continuación definirá la cantidad de almacenamiento y tipo de almacenamiento en base a sus requerimientos')
        #print('     1. CopyOnWrite FileSystem: si no piensa instalar muchos paquetes adicionales (como un switch o router)')
        #print('     2. Raw FileSystem: Si piensa descargar muchos archivos o paquetes (como una base de datos)')
        
        #opcion = self.obtener_int('Seleccionar la opción adecuada para su escenario: ', minValor=1, maxValor=2)
        opcion = fsTest
        
        #print()
        if (opcion):
            if(opcion == 1):
                return {
                    'filesystem': 'CopyOnWrite'
                }
            elif(opcion == 2):
                #tamaño = self.obtener_int('Ingresar la cantidad de almacenamiento (Mínimo:10 GB | Máximo: 80 GB): ', minValor=10, maxValor=80)
                tamaño = sizeTest

                #print()
                if (tamaño):
                    return {
                        'filesystem': 'Raw',
                        'size': tamaño
                    }
                else: 
                    raise InputException()
        else:
            raise InputException()

    def obtener_imagen(self, tabla_imagenes, inputTest:int) -> int:
        '''
            tabla_imagenes: tabla que contiene las imagenes disponibles en el sistema
        '''
        #print(tabla_imagenes)
        #print()
        #imagen_id = self.obtener_int('Ingrese el ID: ')
        imagen_id = inputTest
        #print()
        if(imagen_id):
            return imagen_id
        else:
            raise InputException()

    # Opcion 3: Editar

    def importar_imagen(self, valuesTest:dict) -> dict:
        '''
            Dependiendo de la opcion se retorna:

            opcion 1:
            ---
                {   'opcion':opcion,
                    'nombre':nombre,
                    'categoria':categoria,
                    'ruta':ruta  }

            opcion 2:
            ---
                {   'opcion':opcion,
                    'nombre':nombre,
                    'categoria':categoria,
                    'url':url  }
        '''
        # print('''
        #     1. Seleccionar un archivo local
        #     2. Ingresar un URL para ser descargado por el controlador
        # ''')
        
        #opcion = self.obtener_int('Ingrese la opcion: ', valoresValidos=[1, 2])
        opcion = valuesTest['opcion']

        #nombre = input('\nIngrese un nombre para la imagen: ')
        nombre = valuesTest['nombre']

        categorias_validas = ['server', 'security', 'networking']
        #categoria = input('Ingrese el nombre de la categoria ' +str(categorias_validas)+': ')
        categoria = valuesTest['categoria']

        if (categoria in categorias_validas):
            if (opcion == 1):
                #ruta = input('Ingrese la ruta del archivo: ')
                ruta = valuesTest['ruta']

                return {'opcion': opcion,
                        'nombre': nombre,
                        'categoria': categoria,
                        'ruta': ruta}
            elif (opcion == 2):
                #url = input('Ingrese la url de la imagen: ')
                url = valuesTest['url']

                return {'opcion': opcion,
                        'nombre': nombre,
                        'categoria': categoria,
                        'url': url}
            else:
                raise InputException()
        else:
            raise InputException()

    def agregar_nodo(self, tabla_imagenes:str, valuesTest:dict) -> dict:
        #id_topologia = self.obtener_int('\nIngrese el ID: ')
        id_topologia = valuesTest['id_topologia']
        #print()
        #n_vcpus = self.obtener_numero_vcpus()
        n_vcpus = valuesTest['n_vcpus']
        #memoria = self.obtener_memoria()
        memoria = valuesTest['memoria']
        #filesystem = self.obtener_fs()
        filesystem = valuesTest['filesystem']
        #imagen_id = self.obtener_imagen(tabla_imagenes)
        imagen_id = valuesTest['imagen_id']
        #internet = self.conectar_internet()
        internet = valuesTest['internet']
        return {
            'id_topologia': id_topologia,
            'n_vcpus': n_vcpus,
            'memoria': memoria,
            'filesystem': filesystem,
            'imagen_id': imagen_id,
            'internet': internet
        }

    def aumentar_slice(self, workers_info:str, workers_ids:list, inputTest) -> list:
        '''
            input 
            ---
            workers_info(str): tabla a imprimir con la informacion de los workers 
                                en la infraestructura del slice

            output
            ---
            input_az: lista con los IDs de los workers que se van a añadir al slice
        '''
        #print(workers_info)
        #print('\nElija el(los) worker(s) con los cuales desea aumentar su zona de disponibilidad ')
        #input_az = input('Ingrese los IDs sin espacio y separado por comas (ex: 1001,1002,1003): ')
        input_az = inputTest

        input_az = input_az.split(',')
        if(set(input_az).issubset(workers_ids)):
            # se devuelve la lista de compute-nodes
            # se pasa antes por set() para eliminar duplicados en la lista
            return input_az
        else:
            raise InputException()