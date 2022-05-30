#!/usr/bin/env python3

from ..logging.Exceptions import InputException

from string import printable
from typing import Optional 
from prettytable import PrettyTable

def obtener_int(label, maxValor:Optional[int]=None, minValor:Optional[int]=None, valoresValidos:Optional[list]=None) -> int or False:
    '''
        label: texto a mostrar en la linea de comandos al pedir input

        Devuelve el valor 'integer' si la validacion es satisfactoria, sino se devuelve el booleano 'False'
    '''
    
    variable = input(label)
    if (variable.isdigit()):
        # si es que es un digito
        integer = int(variable)

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
    topologias_validas = ['lineal', 'malla', 'arbol', 'anillo', 'bus']
    variable = input('[?] Ingrese el tipo de topologia '+str(topologias_validas)+': ')
    if(variable in topologias_validas):
            return variable
    else:
        raise InputException()

def obtener_infraestructura() -> str or list:
    '''
        str: Si escoge 'OpenStack' se devuelve el str
        list: Si escoge 'Linux Cluster' se devuelve los workers en los que desea desplegar
    '''

    infraestructuras_validas = ['Linux Cluster', 'OpenStack']
    input_tipo_infraestructura = input('[?] Ingrese el tipo de infraestructura '+str(infraestructuras_validas)+': ')
    if (input_tipo_infraestructura == 'OpenStack'):
        return input_tipo_infraestructura
    elif (input_tipo_infraestructura == 'Linux Cluster'):
        workers_validos = ['worker1', 'worker2', 'worker3']

        print('    Elija el(los) worker(s) donde desea desplegar su zona de disponibilidad '+str(workers_validos)+': ')
        # TODO mostrar metricas de workers (top o /proc/stat)
        # TODO mostrar recursos disponibles en cada worker (en base a la DB) (se muestra vCPUS asignables, memoria asignable y disco libre)

        input_az = input('[?] Ingrese su opcion sin espacio y separado por comas (ej: worker1,worker2): ')
        input_az = input_az.split(',')
        if(set(input_az).issubset(workers_validos)):
            return list(set(input_az)) # se pasa antes por set() para eliminar duplicados en la lista
        else:
            raise InputException()
    else:
        raise InputException()

# Modulo: Administracion

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

    n_vcpus = obtener_int('[?] Ingrese su opcion: ', valoresValidos=valores_validos)
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

    input_memoria = obtener_int('[?] Ingrese su opcion: ', valoresValidos=valores_validos)
    if input_memoria:
        return input_memoria 
    else:
        raise InputException()

def obtener_fs() -> dict or False:
    # TODO se muestra las dos opciones (con sus descripciones): Raw o CopyOnWrite
    # TODO si es usuario escoge Raw se especifica el tamaño (10GB a 80GB) 
    # TODO si el usuario ingresos valores correctos se devuelve un dict con la data
    pass

def obtener_imagen() -> dict:
    '''
        Returns:
            imagen_data (dict): diccionario con el siguiente formato
                {
                    'opcion': 'imagen existente|archivo local|url',

                    ## el resto de parametros varia dependiente de la opcion
                    # opcion 1:
                    'rutaHeadnode': '/ruta/donde/esta/la/imagen/en/headnode'
                    # opcion 2:
                    'rutaLocal': '/de/donde/se/va/a/subir/la/imagen',
                    'rutaHeadnode': '/ruta/donde/se/va/a/subir/la/imagen/en/headnode'
                    # opcion 3:
                    'url': 'http://cirros.img',
                    'rutaHeadnode': '/ruta/donde/se/va/a/descargar/la/imagen/en/headnode'
                }
    '''
    print('[i] Las imagenes disponibles en el sistema son:')
    # TODO se listan de la DB las imagenes disponibles
    print('''
        1. Elegir imagen existente
        2. Importar imagen desde archivo local
        3. Ingresar URL para importar 
    ''')
    opcion = obtener_int('[?] Ingrese la opcion: ', minValor=1, maxValor=3)
    if (opcion == 1):
        # TODO caso: imagen existente
        pass
    elif(opcion == 2):
        # TODO caso: subir archivo local a head node (usar modulo administracion)
        pass
    elif(opcion == 3):
        # TODO caso: descargar url en el headnode (usar modulo administracion)
        pass
    else:
        raise InputException()
