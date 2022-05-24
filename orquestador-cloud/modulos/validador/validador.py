#!/usr/bin/env python3

from typing import Optional 

def obtener_int(texto, maxValor:Optional[int]=None, minValor:Optional[int]=None) -> int or False:
    '''
        texto: texto a mostrar en la linea de comandos

        Devuelve el valor 'integer' si la validacion es satisfactoria, sino se devuelve el booleano 'False'
    '''
    
    variable = input(texto)
    if (variable.isdigit()):
        # si es que es un digito
        integer = int(variable)

        if (maxValor and minValor):
            # si es que se especifico un rango, se valida
            return integer if (minValor <= integer <= maxValor) else False
        else:
            # si no se especifico un rango, se devuelve el entero de frente
            return integer
    else:
        return False