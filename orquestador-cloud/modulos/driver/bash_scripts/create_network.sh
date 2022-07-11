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
if sudo ip netns add ns-$nombre_red; then
    echo [+] Namespace: ns-$nombre_red
fi

# creacion de interfaces veth
sudo ip link add ovs-ns-$nombre_red type veth peer ns-ovs-$nombre_red
sudo ip link set ns-ovs-$nombre_red up
# se asigna un interfaz al ovs
sudo ovs-vsctl add-port $ovs ovs-ns-$nombre_red
sudo ovs-vsctl set port ovs-ns-$nombre_red tag=$vlan_id
sudo ip link set ovs-ns-$nombre_red up
# se asignar la otra interfaz al ns
sudo ip link set ns-ovs-$nombre_red netns ns-$nombre_red

# asignar la ip del dhcp
sudo ip netns exec ns-$nombre_red ip link set ns-ovs-$nombre_red up
sudo ip netns exec ns-$nombre_red ip addr add $ip_dhcp_server dev ns-ovs-$nombre_red
    
# ruta a la red
sudo ip netns exec ns-$nombre_red ip route add $direccion_red dev ns-ovs-$nombre_red

# se ejecuta dnsmasq
touch /home/grupo2/leases_vlan$vlan_id # se crea el archivo donde se guardara los leases
if sudo ip netns exec ns-$nombre_red dnsmasq --dhcp-range=$rango_ip_dhcp --interface=ns-ovs-$nombre_red --dhcp-option=6,8.8.8.8 --dhcp-option=3,$dhcp_gateway --dhcp-leasefile=/home/grupo2/leases_vlan$vlan_id; then
    echo [+] Dnsmasq: /home/grupo2/leases_vlan$vlan_id
    echo [+] DHCP: $ip_dhcp_server, 
    echo [+] Network: $direccion_red
    echo [+] Gateway: $dhcp_gateway
    echo [+] VLAN ID: $vlan_id
fi