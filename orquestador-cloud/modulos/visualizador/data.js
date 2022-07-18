

var topologyData = {
    "links": [
        {
            "mac": "02:00:00:04:aa:8c",
            "source": 88,
            "srcDevice": "a",
            "srcIfName": "link_1",
            "target": -1,
            "tgtDevice": "Bus",
            "tgtIfName": ""
        },
        {
            "mac": "02:00:00:23:26:88",
            "source": 89,
            "srcDevice": "b",
            "srcIfName": "link_1",
            "target": -1,
            "tgtDevice": "Bus",
            "tgtIfName": ""
        },
        {
            "mac": "02:00:00:13:1d:c9",
            "source": 90,
            "srcDevice": "c",
            "srcIfName": "link_1",
            "target": -1,
            "tgtDevice": "Bus",
            "tgtIfName": ""
        }
    ],
    "nodes": [
        {
            "icon": "server",
            "id": 88,
            "name": "a",
            "tunnel_ssh": "ssh -L  5987:127.0.0.1:5987 acceso_vnc@10.20.12.161 -p 2202"
        },
        {
            "icon": "server",
            "id": 89,
            "name": "b",
            "tunnel_ssh": "ssh -L  5988:127.0.0.1:5988 acceso_vnc@10.20.12.161 -p 2201"
        },
        {
            "icon": "server",
            "id": 90,
            "name": "c",
            "tunnel_ssh": "ssh -L  5989:127.0.0.1:5989 acceso_vnc@10.20.12.161 -p 2202"
        },
        {
            "icon": "cloud",
            "id": -1,
            "name": "Bus"
        }
    ]
};