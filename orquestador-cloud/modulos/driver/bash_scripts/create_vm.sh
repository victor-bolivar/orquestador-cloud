#!/bin/bash

vm_name=$1
vlan_id=$2
vnc_port=$3 
image=$4
mac=$5
ruta_fs=$6

ncpus=$7 # numero de vcpus
ram=$8 # memoria ram en GB (ex: 1G)
size=$9 # tamaño en GB (ex: 1G)

ovs_name="ovs"
port_option="$(($vnc_port-5900))" # se resta 5900 para pasalo como option a qemu-system-x86_64
tap_name=$vm_name-vlan$vlan_id


# 1. se crea la interfaz TAP para la VM
if sudo ip tuntap add $tap_name mode tap; then
    echo [+] Interface $tap_name was created SUCCESFULLY
fi
if sudo ip link set $tap_name up;then
    echo [+] Interface $tap_name UP
fi
if sudo ovs-vsctl add-port $ovs_name $tap_name tag=$vlan_id; then
    echo [+] Interfaz $tap_name añadida a $ovs_name en vlan$vlan_id
fi

# 2. se crea la vm
sudo qemu-img create -f qcow2 -o backing_file=$image $ruta_fs $size
if sudo qemu-system-x86_64 -enable-kvm -vnc 0.0.0.0:$port_option \
        -netdev tap,id=$tap_name,ifname=$tap_name,script=no,downscript=no \
        -device e1000,netdev=$tap_name,mac=$mac \
        -daemonize $ruta_fs -cpu host -smp $ncpus -m $ram ; then
    echo [+] Maquina virtual desplegada SATISFACTORIAMENTE en puerto $vnc_port de $(hostname) vlan:$vlan_id
fi
