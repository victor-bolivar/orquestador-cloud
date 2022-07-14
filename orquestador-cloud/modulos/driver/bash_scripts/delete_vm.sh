#!/bin/bash

vm_name=$1
vlan_id=$2
vnc_port=$3 
image=$4
mac=$5
ruta_fs=$6

ovs_name="ovs"
port_option="$(($vnc_port-5900))" # se resta 5900 para pasalo como option a qemu-system-x86_64
tap_name=$vm_name-vlan$vlan_id


# 1. interfaz TAP 
if sudo ip link del $tap_name; then
    echo [+] Interface $tap_name was deleted SUCCESFULLY
fi
if sudo ovs-vsctl del-port $ovs_name $tap_name; then
    echo [+] Interfaz $tap_name removida de $ovs_name en vlan$vlan_id
fi

# 2. eliminar imagen
if rm $ruta_fs; then
    echo [+] Imgen $ruta_fs eliminada SATISFACTORIAMENTE
fi

# eliminar proceso
pid=$(ps -ef | egrep "qemu-system-x86_64 -enable-kvm -vnc 0.0.0.0:${port_option}" | awk '{print $2}' | head -n 1)
if  sudo kill -s SIGKILL $pid; then
    echo [+] Maquina virtual corriendo en puerto $vnc_port eliminado SATISFACTORIAMENTE
fi