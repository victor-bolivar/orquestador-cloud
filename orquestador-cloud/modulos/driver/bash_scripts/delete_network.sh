#!/bin/bash

nombre_red=$1 # ex: vlan100
vlan_id=$2
ovs="ovs"
direccion_red=$3 # ejemplo 192.168.1.0/24
dhcp_gateway=$4 # la primera ip
ip_dhcp_server=$5 # la segunda de la subred (ex: 192.168.1.2/24)
rango_ip_dhcp=$6 # en el formato lowest_ip,highest_ip,netmask por ejemplo 192.168.1.10,192.168.1.254,255.255.255.0
dhcp_gateway_with_netmask=$7 

# se crea el namespace
if sudo ip netns del ns-$nombre_red; then
    echo [+] Namespace eliminado: ns-$nombre_red
fi 

# creacion de interfaces veth
sudo ip link del ovs-ns-$nombre_red 

# se asigna un interfaz al ovs
sudo ovs-vsctl del-port $ovs ovs-ns-$nombre_red

# se ejecuta dnsmasq
rm /home/victor/lab03/leases_vlan$vlan_id 

# verificacion
echo 
sudo ip netns list

# Crear una interfaz interna al OVS con el VLAN ID asignado y se le asignar  ́a laprimera direcci  ́on de la red
sudo ovs-vsctl del-port $ovs vlan$vlan_id 

# verify
echo
sudo ovs-vsctl show

# eliminar proceso
pid=$(ps -ef | grep "dnsmasq --dhcp-range=${rango_ip_dhcp}" | awk '{print $2}'| head -n 1)
if  sudo kill -s SIGKILL $pid; then
    echo [+] DNSMASQ corriendo en namespace ns-$nombre_red eliminado SATISFACTORIAMENTE
fi