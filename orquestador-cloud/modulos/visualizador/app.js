(function (nx) {

    // TODO:
    // 1. para configurar el tooltip (el dropdown menu que sale al hacer click en un nodo) 
    //      añades mas elementos dentro de la lista de: 
    //      nx.define('CustomNodeTooltip', nx.ui.Component, {
    // 1. arriba alianza

    // label interface config
    fontSize = "0.3rem";
    //fontColor = "#1f1f1f";
    fontColor = "#0386d2";
    linkColor = "#0386d2";

    // instantiate NeXt app
    var app = new nx.ui.Application();

    //  extend the standard nx.graphic.Topology.Link class
    nx.define('CustomLinkClass', nx.graphic.Topology.Link, {
        properties: {
            sourcelabel: null,
            targetlabel: null
        },
        view: function (view) {
            view.content.push({
                name: 'source',
                type: 'nx.graphic.Text',
                props: {
                    'class': 'sourcelabel',
                    'alignment-baseline': 'text-after-edge',
                    'text-anchor': 'start',
                    "font-size": fontSize,
                    "fill": fontColor
                }
            }, {
                name: 'target',
                type: 'nx.graphic.Text',
                props: {
                    'class': 'targetlabel',
                    'alignment-baseline': 'text-after-edge',
                    'text-anchor': 'end',
                    "font-size": fontSize,
                    "fill": fontColor
                }
            });
            return view;
        },
        methods: {
            update: function () {
                this.inherited();
                var el, point;
                var line = this.line();
                var angle = line.angle();
                var stageScale = this.stageScale();
                line = line.pad(18 * stageScale, 18 * stageScale);
                if (this.sourcelabel()) {
                    el = this.view('source');
                    point = line.start;
                    el.set('x', point.x + 1);
                    el.set('y', point.y - 1);
                    el.set('text', this.sourcelabel());
                    el.set('transform', 'rotate(' + angle + ' ' + point.x + ',' + point.y + ')');
                    el.setStyle('font-size', 12 * stageScale);
                }
                if (this.targetlabel()) {
                    el = this.view('target');
                    point = line.end;
                    el.set('x', point.x - 1);
                    el.set('y', point.y - 1);
                    el.set('text', this.targetlabel());
                    el.set('transform', 'rotate(' + angle + ' ' + point.x + ',' + point.y + ')');
                    el.setStyle('font-size', 12 * stageScale);
                }
            }
        }
    });

    // extend the tooltip (when clicking on a node)
    nx.define('CustomNodeTooltip', nx.ui.Component, {
        properties: {
            node: {},
            topology: {}
        },
        view: {
            content: [{
                tag: 'div',
                content: [{
                    tag: 'h5',
                    content: [{
                        tag: 'a',
                        content: '{#node.model.name}',
                        props: { "href": "{#node.model.vncLink}" }
                    }],
                    props: {
                        "style": "border-bottom: dotted 1px; font-size:90%; word-wrap:normal; color:#003688"
                    }
                }, {
                    tag: 'p',
                    content: [
                        {
                            tag: 'label',
                            content: 'Management: ',
                        }, {
                            tag: 'label',
                            content: '{#node.model.Management}',
                        }
                    ],
                    props: {
                        "style": "font-size:80%;"
                    }
                },
                ],
                props: {
                    "style": "width: 150px;"
                }
            }]
        }
    });

    nx.define('Tooltip.Node', nx.ui.Component, {
        view: function (view) {
            view.content.push({
            });
            return view;
        },
        methods: {
            attach: function (args) {
                this.inherited(args);
                this.model();
            }
        }
    });

    // configuration object for next
    var topologyConfig = {
        // set dimensions
        width: 1200,
        height: 700,
        // Node and Link identity key attribute name
        identityKey: 'id',
        // moves the labels in order to avoid overlay
        'enableSmartLabel': true,
        // smooth scaling. may slow down, if true
        'enableGradualScaling': true,
        // if true, two nodes can have more than one link
        'supportMultipleLink': true,
        // enable scaling
        "scalable": true,


        // special configuration for nodes
        "nodeConfig": {
            "label": "model.name",
            "iconType": "model.icon"

        },
        // if true, the nodes' icons are shown, otherwise a user sees a dot instead
        "showIcon": true,
        // automatically compute the position of nodes
        "dataProcessor": "force",

        // Configuration of the extended link config
        linkConfig: {
            linkType: 'curve',
            sourcelabel: 'model.srcIfName',
            targetlabel: 'model.tgtIfName',
            color: linkColor
        },
        // Use extended link class version with interface labels enabled
        linkInstanceClass: 'CustomLinkClass',

        // Configuration of the extended tooltip (when clicking on a node)
        tooltipManagerConfig: {
            nodeTooltipContentClass: 'CustomNodeTooltip'
        },

    };


    // instantiate Topology class
    var topology = new nx.graphic.Topology(topologyConfig);

    // load topology data from app/data.js
    topology.data(topologyData);

    // bind the topology object to the app
    topology.attach(app);

    // app must run inside a specific container. In our case this is the one with id="topology-container"
    app.container(document.getElementById("topology-container"));

})(nx);