#!/usr/bin/env python3

from ast import Str
import re
import string
from ..logging.Exceptions import InputException

from string import printable
from typing import Optional 
from prettytable import PrettyTable

# Funciones base
def obtener_int(label, maxValor:Optional[int]=None, minValor:Optional[int]=None, valoresValidos:Optional[list]=None) -> int or False:
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
    
# Modulo: Menu

def obtener_tipo_topologia() -> str:
    topologias_validas = ['(1)lineal', '(2)malla', '(3)arbol', '(4)anillo', '(5)bus']
    variable = obtener_int('Ingrese el tipo de topologia '+str(topologias_validas)+': ', minValor=1, maxValor=5)
    if(variable==1):
        return 'lineal'
    elif(variable==2):
        return 'malla'
    elif(variable==3):
        return 'arbol'
    elif(variable==4):
        return 'anillo'
    elif(variable==5):
        return 'bus'
    else:
        raise InputException()

def obtener_infraestructura() -> str or list:
    '''
        str: Si escoge 'OpenStack' se devuelve el str
        list: Si escoge 'Linux Cluster' se devuelve los workers en los que desea desplegar
    '''

    infraestructuras_validas = ['(1)Linux Cluster', '(2)OpenStack']
    input_tipo_infraestructura = obtener_int('Ingrese el tipo de infraestructura '+str(infraestructuras_validas)+': ', valoresValidos=[1,2])
    if (input_tipo_infraestructura == 2):
        # caso: openstack
        return input_tipo_infraestructura
    elif (input_tipo_infraestructura == 1):
        # caso: linux cluster
        workers_validos = ['worker1', 'worker2', 'worker3']
        print('Elija el(los) worker(s) donde desea desplegar su zona de disponibilidad ')
        # TODO mostrar metricas de workers (top o /proc/stat)
        # TODO mostrar recursos disponibles en cada worker (en base a la DB) (se muestra vCPUS asignables, memoria asignable y disco libre)
        x3 = PrettyTable()
        x3.field_names = ["Nombre", "Porcentaje de uso de CPU", "cantidad disponible de vCPU", "cantidad de memoria libre", "cantidad de disco libre"]
        x3.add_row(["Worker1", "30 %" , 16, "3 GB", "20 GB"])
        x3.add_row(["Worker2", " 50 %", 10, "2 GB", "15 GB"])
        x3.add_row(["Worker3", " 60 %", 12, "2 GB", "10 GB"])
        x3 = '\n'+ str(x3)
        x3 = x3.replace("\n", "\n                ")
        print(x3)
        print('')
        input_az = input('Ingrese su opcion sin espacio y separado por comas '+str(workers_validos)+': ')
        input_az = input_az.split(',')
        if(set(input_az).issubset(workers_validos)):
            # se devuelve la lista de compute-nodes
            return list(set(input_az)) # se pasa antes por set() para eliminar duplicados en la lista
        else:
            raise InputException()
    else:
        raise InputException()

# Creacion de VM

def obtener_numero_vcpus() -> int or False:
    valores_validos = [1, 2, 4, 8]

    print('Elija el número de vCPUs')
    # se imprime la tabla
    t = PrettyTable(valores_validos)
    t.padding_width = 1
    t.title = 'vCPUs'
    t = str(t)[:str(t).rfind('\n')] # modificacion para que no se vea la ultima linea
    # para añadir identacion a la tabla
    t = '                '+t
    t = t.replace("\n", "\n                ")
    print(t) 

    n_vcpus = obtener_int('Ingrese su opción: ', valoresValidos=valores_validos)
    print()
    if n_vcpus:
        return n_vcpus 
    else:
        raise InputException()
    
def obtener_memoria() -> int:
    valores_validos = [1, 2, 4, 8]

    print('Elija el tamaño de la memoria')
    # se imprime la tabla
    t = PrettyTable(valores_validos)
    t.padding_width = 1
    t.title = 'Memoria (GB)'
    t = str(t)[:str(t).rfind('\n')] # modificacion para que no se vea la ultima linea
    # para añadir identacion a la tabla
    t = '                '+t
    t = t.replace("\n", "\n                ")
    print(t) 

    input_memoria = obtener_int('Ingrese su opción: ', valoresValidos=valores_validos)
    print()
    if input_memoria:
        return input_memoria 
    else:
        raise InputException()
def obtener_almacenamiento()-> int:
    print('A continuación definirá la cantidad de almacenamiento y tipo de almacenamiento en base a sus requerimientos')
    print('     1. Si no piensa instalar muchos paquetes adicionales (como un switch o router)')
    print('     2. Si piensa descargar muchos archivos o paquetes (como una base de datos)') 
    var123 = obtener_int('Seleccionar la opción adecuada para su escenario: ', minValor=1, maxValor=2)
    print()
    if (var123):
        if(var123 == 1):
            return var123
        elif(var123 == 2):
            almac1 = input('Ingresar la cantidad de almacenamiento (Mínimo:10 GB | Máximo: 80 GB):')
            print()
            return var123
        pass
    else:
        print('[x] Ingrese una opción válida')

def obtener_imagenvm() -> int:
    x3 = PrettyTable()
    x3.field_names = ["ID", "Tipo de imagen", "Nombre"]
    x3.add_row([1,"Networking", "CiscoIoS"])
    x3.add_row([2,"Networking", "CiscoIOS XRv"])
    x3.add_row([3,"Server", "Ubuntu 20.04"])
    x3.add_row([4,"Server", "Ubuntu 18.04"])
    x3 = str(x3)
    x3 = x3.replace("\n", "\n                ")
    x3 = '                '+x3
    print('Lista de imágenes disponibles')
    print(x3)
    print('Seleccione la imagen para la VM')
    ima1 = obtener_int('Ingrese el ID: ', minValor=1, maxValor=4)
    print()
    opcion110 = input('Ingresar el nombre de la VM: ')
    print()
    if(ima1):
        return ima1
    else:
        print('[x] Ingrese una opción válida')    

def obtener_keypair() -> int:
    x345 = PrettyTable()
    x345.field_names = ["Opción", "Nombre"]
    x345.add_row([1, "Key pair 1" ])
    x345.add_row([2, "Key pair 2"])
    x345.add_row([3, "Key pair 3"])
    x345.add_row([4, "Key pair 4"])
    x345 = str(x345)
    x345 = x345.replace("\n", "\n                ")
    x345 = '                '+x345
    print('Lista de keypairs')
    print(x345)
    keypair1 = obtener_int('Ingrese el ID: ', minValor=1, maxValor=4)
    if(keypair1):
        if(keypair1 == 1 or keypair1 == 2 or keypair1 == 3 or keypair1 == 4):
            return keypair1
    else:
        print('[x] Ingrese una opción válida')

def conectar_internet() -> int:
    print('¿Desea que la topología tenga conexión a Internet?')
    print('     1. Sí ')
    print('     2. No ')
    keypair1 = obtener_int('Ingrese la opción: ', minValor=1, maxValor=2)
    print()
    if (keypair1):
        return keypair1
        pass
    else:
        print('[x] Ingrese una opción válida')

def obtener_fs() -> dict or False:
    # TODO se muestra las dos opciones (con sus descripciones): Raw o CopyOnWrite
    # TODO si es usuario escoge Raw se especifica el tamaño (10GB a 80GB) 
    # TODO si el usuario ingresos valores correctos se devuelve un dict con la data
    pass

# Importar 

def obtener_imagen() -> dict:
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
    opcion = obtener_int('Ingrese la opcion: ', valoresValidos=[1,2])
    nombre = input('Ingrese un nombre para la imagen: ')
    categorias_validas = ['server','security','networking']
    categoria = input('Ingrese el nombre de la categoria '+str(categorias_validas)+': ')
    if (opcion == 1):
        ruta = input('Ingrese la ruta del archivo: ')
        return {'opcion':opcion,
                'nombre':nombre,
                'categoria':categoria,
                'ruta':ruta}
    elif (opcion == 2):
        url = input('Ingrese la url de la imagen: ') 
        return {'opcion':opcion,
                'nombre':nombre,
                'categoria':categoria,
                'url':url}

def input_crear_topologia():
    pass

def id_topologia_eliminar() -> int:
    x33 = PrettyTable()
    x33.field_names = ["ID",  "Nombre"]
    x33.add_row(["1", "TopologiíaPrueba"])
    x33.add_row(["2", "TopologíaTest"])
    x33.add_row(["3", "Topología1"])
    x33.add_row(["4", "Topología Bus"])
    x33.add_row(["5", "Topología anillo"])
    x33.add_row(["6", "Topología 3 nodos"])
    x33.add_row(["7", "Topología 4"])
    x33 = '\n'+ str(x33)
    x33 = x33.replace("\n", "\n                ")
    print('''\nLista de las topologías actuales'''   
    )
    print(x33)
    print('')   
    opcion1 = obtener_int('Ingrese el ID: ', minValor=1, maxValor=7)
    if(opcion1):
        if (opcion1 == 1 or opcion1 == 2 or opcion1 == 3 or opcion1 == 4 or opcion1 == 5
            or opcion1 == 6 or opcion1 == 7 ):
            print()
            return opcion1
        else:
                        # Si no se especifico una opcion valida, se procede con el bucle
            print('[x] Ingrese una opción válida')
    else:
                        # Si no se especifico una opcion valida, se procede con el bucle
        print('[x] Ingrese una opción válida')

def id_topologia_nodo_adicional () -> int:
    x23 = PrettyTable()
    x23.field_names = ["ID",  "Nombre"]
    x23.add_row(["1", "TopologiíaPrueba"])
    x23.add_row(["2", "TopologíaTest"])
    x23.add_row(["4", "Topología Bus"])
    x23.add_row(["5", "Topología anillo"])
    x23.add_row(["6", "Topología 3 nodos"])
    x23.add_row(["7", "Topología 4"])
    x23 = '\n'+ str(x23)
    x23 = x23.replace("\n", "\n                ")
    print('''\nA continuación se listan las topologías actuales:'''   
    )
    print(x23)
    print('')
    opcion1 = obtener_int('Ingrese la opción: ', minValor=1, maxValor=7)

    if(opcion1):
        if (opcion1 == 1 or opcion1 == 2 or opcion1 == 3 or opcion1 == 4 or opcion1 == 5
            or opcion1 == 6):
            workers_validos = ['worker1', 'worker2', 'worker3']
            x23 = PrettyTable()
            x23.field_names = ["ID",  "Nombre"]
            x23.add_row(["1", "Nodo 1"])
            x23.add_row(["2", "Nodo 2"])
            x23.add_row(["4", "Nodo 3"])
            x23 = '\n'+ str(x23)
            x23 = x23.replace("\n", "\n                ")
            print('''\nA continuación se listan los nodos actuales:'''   
            )
            print(x23)
            print('')

            n_vcpus = obtener_numero_vcpus()
            memoria = obtener_memoria()
            print('A continuación definirá la cantidad de almacenamiento y tipo de almacenamiento en base a sus requerimientos')
            print('     1. Si piensa usar dicha VM como un switch (donde no instalaria muchos paquetes adicionales)')
            print('     2. Si planea usar la máquina como una base de datos o una máquina virtual donde constantemente se descargarìa archivos de gran tamaño)') 
            var123 = obtener_int('Seleccionar la opción adecuada para su escenario: ', minValor=1, maxValor=2)

            if (var123):
                if(var123 == 2):
                    almac1 = input('Ingresar la cantidad de almacenamiento (Mínimo:10 GB | Máximo: 80 GB):')
                    x3 = PrettyTable()
                    x3.field_names = ["Opción", "Tipo de imagen", "Nombre"]
                    x3.add_row([1,"Networking", "CiscoIoS"])
                    x3.add_row([2,"Networking", "CiscoIOS XRv"])
                    x3.add_row([3,"Server", "Ubuntu 20.04"])
                    x3.add_row([4,"Server", "Ubuntu 18.04"])
                    x3 = '\n'+ str(x3)
                    x3 = x3.replace("\n", "\n                ")
                    print('Lista de imágenes disponibles')
                    print(x3)
                    print()
                    print('Seleccione la imagen para la VM')
                    ima1 = obtener_int('Ingrese el ID: ', minValor=1, maxValor=4)
                    opcion110 = input('Ingresar el nombre de la VM:')
                    x345 = PrettyTable()
                    x345.field_names = ["Opción", "Nombre"]
                    x345.add_row([1, "Key pair 1" ])
                    x345.add_row([2, "Key pair 2"])
                    x345.add_row([3, "Key pair 3"])
                    x345.add_row([4, "Key pair 4"])
                    x345 = '\n'+ str(x345)
                    x345 = x345.replace("\n", "\n                ")
                    print('''\nLista de Key Pair''')
                    print(x345)
                    print()
                    print('Seleccione el key pair para el acceso a la VM')
                    keypair1 = obtener_int('Ingrese el ID: ', minValor=1, maxValor=4)

                    if(keypair1):
                        if(keypair1 == 1 or keypair1 == 2):
                            return keypair1
                    else:
                        print('[x] Ingrese una opción válida')
                
            else:
                print('[x] Ingrese una opción válida')

def validar_eliminar_nodo() -> int:
    x33 = PrettyTable()
    x33.field_names = ["ID",  "Nombre"]
    x33.add_row(["1", "TopologiíaPrueba"])
    x33.add_row(["2", "TopologíaTest"])
    x33.add_row(["3", "Topología1"])
    x33.add_row(["4", "Topología Bus"])
    x33.add_row(["5", "Topología anillo"])
    x33.add_row(["6", "Topología 3 nodos"])
    x33.add_row(["7", "Topología 4"])
    x33 = '\n'+ str(x33)
    x33 = x33.replace("\n", "\n                ")
    print('''\nA continuacion se listan las topologías''')
    print(x33)
    print('')               
    opcion1 = obtener_int('Ingrese el ID: ', minValor=1, maxValor=7)

    if(opcion1):
        if (opcion1 == 1 or opcion1 == 2 or opcion1 == 3 or opcion1 == 4 or opcion1 == 5
            or opcion1 == 6):
                x23 = PrettyTable()
                x23.field_names = ["ID",  "Nombre"]
                x23.add_row(["1", "Nodo 1"])
                x23.add_row(["2", "Nodo 2"])
                x23.add_row(["3", "Nodo 3"])
                x23.add_row(["4", "Nodo 4"])
                x23 = '\n'+ str(x23)
                x23 = x23.replace("\n", "\n                ")
                print('')
                print('Lista de los nodos')
                print(x23)
                print('')
                opcion1 = obtener_int('Ingrese el ID: ', minValor=1, maxValor=4)
                if(opcion1):
                            if(opcion1 == 1 or opcion1 == 2 or opcion1 == 3 or opcion1 == 4):
                                return opcion1 
                else:
                                print('[x] Ingrese una opción válida')
    else:
        print('[x] Ingrese una opción válida')

    pass

def validar_aumentar_slice() -> int:

    x33 = PrettyTable()
    x33.field_names = ["ID",  "Nombre"]
    x33.add_row(["1", "TopologiíaPrueba"])
    x33.add_row(["2", "TopologíaTest"])
    x33.add_row(["3", "Topología1"])
    x33.add_row(["4", "Topología Bus"])
    x33.add_row(["5", "Topología anillo"])
    x33.add_row(["6", "Topología 3 nodos"])
    x33.add_row(["7", "Topología 4"])
    x33 = '\n'+ str(x33)
    x33 = x33.replace("\n", "\n                ")
    print('\nSeleccionar la topología que desea expandir la capacidad'  )
    print(x33)
    print('')
    opcion22 = obtener_int('Ingrese el ID: ', minValor=1, maxValor=7)
    print('')
    x93 = PrettyTable()
    x93.field_names = ["Opción",  "Nombre"]
    x93.add_row(["1", "worker1"])
    x93 = '\n'+ str(x93)
    x93 = x93.replace("\n", "\n                ")
    print('A continuación se muestra el/los worker(s) donde se encuentra la topología: ')
    print(x93)
    print('')
    if(opcion22 == 1 or opcion22 == 2 or opcion22 == 3 or opcion22 == 4 or opcion22 == 5 or
        opcion22 == 6):

        print('Se presentan los workers actuales y sus respectivas capacidades disponibles ')
        x3 = PrettyTable()
        x3.field_names = ["Nombre", "Porcentaje de uso de CPU", "cantidad disponible de vCPU", "cantidad de memoria libre", "cantidad de disco libre"]
        x3.add_row(["Worker1", "30 %" , 16, "3 GB", "20 GB"])
        x3.add_row(["Worker2", " 50 %", 10, "2 GB", "15 GB"])
        x3.add_row(["Worker3", " 60 %", 12, "2 GB", "10 GB"])
        x3 = '\n'+ str(x3)
        x3 = x3.replace("\n", "\n                ")
        print(x3)
        print('')
        input_az = input('Ingrese su opción sin espacio y separado por comas (ej: worker1,worker2): ')
        input_az = input_az.split(',')
                    
        return opcion22
    else:
        print('[x] Ingrese una opción válida')


def validar_conectividad() -> int:
    print('''\nA continuación de listan las topologías actuales:
        1. Conexión a Internet
        2. Conexión entre topologías'''   
    )
    opcion1 = obtener_int('Ingrese la opción: ', minValor=1, maxValor=7)
    if (opcion1):
        if (opcion1 == 1):
            x44 = PrettyTable()
            x44.field_names = ["ID",  "Nombre","Redes"]
            x44.add_row(["1", "TopologiíaPrueba", "192.168.0.0/24, 192.168.2.0/24"])
            x44.add_row(["2", "TopologíaTest", "172.16.0.0/24, 172.16.10.0/24"])
            x44.add_row(["3", "Topología1", "10.0.0.0/8"])
            x44.add_row(["4", "Topología Bus", "10.0.0.0/10"])
            x44.add_row(["5", "Topología anillo", "172.16.0.0/12"])
            x44.add_row(["6", "Topología 3 nodos", "192.168.0.0/16"])
            x44.add_row(["7", "Topología 4","10.0.0.0/24" ])
            x44 = '\n'+ str(x44)
            x44 = x44.replace("\n", "\n                ")
            print('\nSeleccionar la topología que desea conectar a Internet')
            print(x44)
            print('')
            opcion2 = obtener_int('Ingrese el ID: ', minValor=1, maxValor=7)
            if (opcion2 == 1 or opcion2 == 2 or opcion2 == 3 or opcion2 == 4 or opcion2 == 5
                or opcion2 == 6 or opcion2 == 7):
                return opcion2
            else:
                print('[x] Ingrese una opción válida') 
            
        elif ( opcion1 == 2):
            x55 = PrettyTable()
            x55.field_names = ["ID",  "Nombre","Red"]
            x55.add_row(["1", "TopologiíaPrueba", "192.168.0.0/20"])
            x55.add_row(["2", "TopologíaTest", "172.16.0.0/24"])
            x55.add_row(["3", "Topología1", "10.0.0.0/8"])
            x55.add_row(["4", "Topología Bus", "10.0.0.0/10"])
            x55.add_row(["5", "Topología anillo", "172.16.0.0/12"])
            x55.add_row(["6", "Topología 3 nodos", "192.168.0.0/16"])
            x55.add_row(["7", "Topología 4","10.0.0.0/24" ])
            x55 = '\n'+ str(x55)
            x55 = x55.replace("\n", "\n                ")
            print('''\nSeleccionar las topologías que desean conectar
                    ''')
            print(x55)
            print('')
            opcion12 = obtener_int('Ingrese el ID: ', minValor=1, maxValor=6)
            opcion13 = obtener_int('Ingrese el ID: ', minValor=1, maxValor=6)
            if (opcion12 == 1 or opcion12 == 2 or opcion12 == 3 or opcion12 == 4 or opcion12 == 5
                or opcion12 == 6):
                        return opcion12
            else:
                print('[x] Ingrese una opción válida') 

        else:
            print('[x] Ingrese una opción válida') 
        pass
    else:
        print('[x] Ingrese una opción válida')

def validar_keypair()-> str:
    print('')
    ruta = input('Ingrese la ruta del archivo: ')
    nombre = input('Ingrese el nombre de Key Pair: ')
    return nombre