#!/usr/bin/env python3

import warnings
from cryptography.utils import CryptographyDeprecationWarning
with warnings.catch_warnings():
    warnings.filterwarnings('ignore', category=CryptographyDeprecationWarning)
    import paramiko
from datetime import datetime, timedelta

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

    def ejecutar_comando(self, comando) -> str:
        # initialize the SSH client
        client = paramiko.SSHClient()
        # add to known hosts
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=self.host, port=self.puerto, username=self.username, key_filename=self.private_key, passphrase=self.passphrase)
        # execute
        stdin, stdout, stderr = client.exec_command(comando)
        print(stdout.read().decode())
        if stdout.channel.recv_exit_status() == 0:
            return stdout
        else:
            raise Exception(str(stderr.read().decode()))
    
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
        if stdout.channel.recv_exit_status() == 0:
            print(stderr.read().decode())
            return stdout
        else:
            raise Exception('error en la ejecucion de script | '+str(stderr.read().decode()))

    def leer_csv(self, remote_file):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=self.host, port=self.puerto, username=self.username, key_filename=self.private_key, passphrase=self.passphrase)
        sftp = client.open_sftp()
        remote_file = sftp.open(remote_file)
        try:
            csv_list = []
            for line in remote_file:
                line = line.rstrip() # remover \n
                line = line.split(',') # csv 
                csv_list.append(line)
        finally:
            remote_file.close()
        sftp.close()
        client.close()
        return csv_list

    # Funciones de uso especifico
    
    def list_cpu_usage(self, filename) -> list:
        csv_list = self.leer_csv(filename)
        # se considera solo las mediciones de los ultimos 5 dias
        list_cpu_usage = [] # donde se almacenara las metricas de los ultimos 5 dias
        days = 5
        last_date = datetime.strptime(csv_list[-1][0], "%Y-%m-%d %H:%M:%S")
        for [date,cpu_usage] in csv_list:
            if (datetime.strptime(date, "%Y-%m-%d %H:%M:%S") + timedelta(days=days) > last_date):
                list_cpu_usage.append(cpu_usage)
        return list_cpu_usage
        