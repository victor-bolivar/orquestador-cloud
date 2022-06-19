#!/usr/bin/env python3

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
        workers_validos = ['compute-1', 'compute-2', 'compute-3']
        print('    Elija el(los) worker(s) donde desea desplegar su zona de disponibilidad '+str(workers_validos)+': ')
        # TODO mostrar metricas de workers (top o /proc/stat)
        # TODO mostrar recursos disponibles en cada worker (en base a la DB) (se muestra vCPUS asignables, memoria asignable y disco libre)
        input_az = input('Ingrese su opcion sin espacio y separado por comas (ej: compute-1,compute-2): ')
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

    print('    Elija el numero de vCPUs')
    # se imprime la tabla
    t = PrettyTable(valores_validos)
    t.padding_width = 1
    t.title = 'vCPUs'
    t = str(t)[:str(t).rfind('\n')] # modificacion para que no se vea la ultima linea
    # para añadir identacion a la tabla
    t = '                '+t
    t = t.replace("\n", "\n                ")
    print(t) 

    n_vcpus = obtener_int('Ingrese su opcion: ', valoresValidos=valores_validos)
    if n_vcpus:
        return n_vcpus 
    else:
        raise InputException()
    
def obtener_memoria() -> int:
    valores_validos = [1, 2, 4, 8]

    print('    Elija el tamaño de la memoria')
    # se imprime la tabla
    t = PrettyTable(valores_validos)
    t.padding_width = 1
    t.title = 'Memoria (GB)'
    t = str(t)[:str(t).rfind('\n')] # modificacion para que no se vea la ultima linea
    # para añadir identacion a la tabla
    t = '                '+t
    t = t.replace("\n", "\n                ")
    print(t) 

    input_memoria = obtener_int('Ingrese su opcion: ', valoresValidos=valores_validos)
    if input_memoria:
        return input_memoria 
    else:
        raise InputException()

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