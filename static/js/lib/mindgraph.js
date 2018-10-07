/**
 * Created by khoroshenkikh on 01.05.17.
 */

var __MindGraphConstants = {
    colors : ['#7D8A2E', '#C9D787', '#FFC0A9', 'FF8598'],
    emptyNodeColor : '#FFFFFF'
};

var MindGraph = {
    // graphData: undefined,
    init : function (inputGraphData) {
        var self = this;

        var clusters = inputGraphData.repr || inputGraphData;
        var graph_data = {
            nodes: [],
            edges: []
        };
        var COLORS = __MindGraphConstants.colors;
        self.seen_nodes = {};
        for (i_cluster in clusters) {
            var data = clusters[i_cluster];
            var color = COLORS[i_cluster % COLORS.length];
            for (node in data.nodes) {
                if (!self.seen_nodes[node]) {
                    var node_attrs = data.nodes[node];

                    var label = node_attrs.text || node;

                    // Node without additional information is white
                    var node_color = __MindGraphConstants.emptyNodeColor;

                    if (node_attrs.html) {
                        node_color = color;
                    }
                    var page_rank_scale = 50.;
                    var node_obj = {
                        'id': node,
                        'label': label,
                        'shape': 'box',
                        'color': node_color,
                        'mass': 10,
                        'font': {
                            'size': 50 * Math.log(
                                page_rank_scale * Math.max(
                                    2./page_rank_scale,
                                    data.nodes[node]['page_rank']
                                )
                            )
                        }
                    };
                    if (data.nodes[node]['is_root']) {
                        node_obj.mass *= 2;
                        node_obj.font = {'size': 20};
                    }
                    graph_data.nodes.push(node_obj);
                    self.seen_nodes[node] = node_attrs;
                }
            }
            for (from in data.edges) {
                for (to in data.edges[from]) {
                    var attrs = data.edges[from][to];
                    var edge_obj = {'from': from, 'to': to, 'color': color};
                    if (attrs.layout === 'tree') {
                        edge_obj.arrows = 'to';
                    }
                    graph_data.edges.push(edge_obj);
                }
            }
        }
        self.graphData = graph_data;

        return self;
    },
    selectedNode: undefined,
    getSelectedNodeInfo: function () {
        var self = this;
        if (!self.seen_nodes) {
            return "";
        }
        var attrs = self.seen_nodes[self.selectedNode];
        if (!attrs) {
            return "";
        }
        return "<h4>'"+self.selectedNode+"' info:</h4>" + attrs.html;
    },
    createNetwork: function (networkElementId, selectedNodeElementID) {
        var self = this;

        var container = document.getElementById(networkElementId);
        var options = {};
        var network = new vis.Network(container, self.graphData, options);

        network.on("selectNode", function(params) {
            var node = params.nodes[0];
            self.selectedNode = node;
            document.getElementById(selectedNodeElementID).innerHTML = self.getSelectedNodeInfo();
        });

        return network;
    }
};