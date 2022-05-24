// icon: unknown, switch, router, server, phone, host, cloud, firewall

var topologyData = {
    "nodes": [
        {
            "id": 0,
            "name": "PC0",
            "icon": "host",
            "Management": "192.168.0.10/24",
            "vncLink": "https://tipo.vnrt/token=?"
        },
        {
            "id": 1,
            "name": "PC1",
            "icon": "host",
            "Management": "192.168.0.10/24",
            "vncLink": "https://tipo.vnrt/token=?"
        },
        {
            "id": 2,
            "name": "PC2",
            "icon": "host",
            "Management": "192.168.0.10/24",
            "vncLink": "https://tipo.vnrt/token=?"
        }
    ],
    "links": [
        {
            "source": 0,
            "target": 1,

            "srcDevice": "PC0",
            "tgtDevice": "PC1",

            "srcIfName": "ens1",
            "tgtIfName": "ens3"
        },
        {
            "source": 0,
            "target": 2,

            "srcDevice": "PC0",
            "tgtDevice": "PC2",

            "srcIfName": "ens2",
            "tgtIfName": "ens3"
        }
    ]
};