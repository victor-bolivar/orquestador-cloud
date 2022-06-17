#!/usr/bin/env python3

import warnings
from cryptography.utils import CryptographyDeprecationWarning
with warnings.catch_warnings():
    warnings.filterwarnings('ignore', category=CryptographyDeprecationWarning)
    import paramiko

class SSH:
    def __init__(self, host, puerto, username, private_key, passphrase):
        self.puerto = puerto
        self.host = host
        self.username = username
        self.private_key = private_key # ubicacion de la llave (ex: './id_ecdsa')
        self.passphrase = passphrase # passphrase de la llave

    def subir_archivo(self, local_file, remote_file):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=self.host, port=self.puerto, username=self.username, key_filename=self.private_key, passphrase=self.passphrase)
        sftp = client.open_sftp()
        sftp.put(local_file, remote_file)
        sftp.close()
        client.close()

    def ejecutar_comando(self, comando):
        # initialize the SSH client
        client = paramiko.SSHClient()
        # add to known hosts
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=self.host, port=self.puerto, username=self.username, key_filename=self.private_key, passphrase=self.passphrase)
        # execute
        stdin, stdout, stderr = client.exec_command(comando)
        print(stdout.read().decode())
        err = stderr.read().decode()
        if err:
            print(err)
    
    def ejecutar_script_local(self, script:str, argumentos:list):
        with open(script, "r") as f:
            mymodule = f.read()

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=self.host, port=self.puerto, username=self.username, key_filename=self.private_key, passphrase=self.passphrase)

        argumentos_str=' '.join(argumentos) # se pasa la lista de argumento a un string separados por espacios en blanco ' '
        command = "/bin/bash -s {arg}".format(arg=argumentos_str)
        stdin, stdout, stderr = client.exec_command(command)
        stdin.write(mymodule)
        stdin.close()
        # imprimir stdout / stderr
        print(stdout.read().decode())
        err = stderr.read().decode()
        if err:
            print(err)