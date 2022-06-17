#!/usr/bin/env python3

# TODO definir un formato mas adecuado para logs

class InputException(Exception):
    def __init__(self, inputIngresado=None, mensaje="[x] Ingrese una opcion valida"):
        self.inputIngresado = inputIngresado # se usara para loguear errores de ser necesario
        self.mensaje = mensaje # opcionalmente, se puede recibir un mensaje mas especifico
        super().__init__(self.mensaje)
    