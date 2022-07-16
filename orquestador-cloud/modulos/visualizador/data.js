

var topologyData = {
    "links": [
        {
            "mac": "02:00:00:84:dc:ab",
            "source": 75,
            "srcDevice": "vm1",
            "srcIfName": "link_1",
            "target": -1,
            "tgtDevice": "Bus",
            "tgtIfName": ""
        },
        {
            "mac": "02:00:00:6a:d4:e7",
            "source": 76,
            "srcDevice": "vm2",
            "srcIfName": "link_1",
            "target": -1,
            "tgtDevice": "Bus",
            "tgtIfName": ""
        },
        {
            "mac": "02:00:00:d3:c4:4a",
            "source": 77,
            "srcDevice": "vm3",
            "srcIfName": "link_1",
            "target": -1,
            "tgtDevice": "Bus",
            "tgtIfName": ""
        },
        {
            "mac": "02:00:00:0c:02:b1",
            "source": 78,
            "srcDevice": "vmz",
            "srcIfName": "link_1",
            "target": -1,
            "tgtDevice": "Bus",
            "tgtIfName": ""
        }
    ],
    "nodes": [
        {
            "icon": "server",
            "id": 75,
            "name": "vm1",
            "tunnel_ssh": "ssh -L  5974:127.0.0.1:5974 acceso_vnc@10.20.12.161 -p 2201"
        },
        {
            "icon": "server",
            "id": 76,
            "name": "vm2",
            "tunnel_ssh": "ssh -L  5975:127.0.0.1:5975 acceso_vnc@10.20.12.161 -p 2201"
        },
        {
            "icon": "server",
            "id": 77,
            "name": "vm3",
            "tunnel_ssh": "ssh -L  5976:127.0.0.1:5976 acceso_vnc@10.20.12.161 -p 2201"
        },
        {
            "icon": "server",
            "id": 78,
            "name": "vmz",
            "tunnel_ssh": "ssh -L  5977:127.0.0.1:5977 acceso_vnc@10.20.12.161 -p 2202"
        },
        {
            "icon": "cloud",
            "id": -1,
            "name": "Bus"
        }
    ]
};