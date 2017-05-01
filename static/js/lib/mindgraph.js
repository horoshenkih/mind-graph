/**
 * Created by khoroshenkikh on 01.05.17.
 */

var mindGraphConstants = {
    colors : ['#F19CBB', '#7CB9E8', '#B0BF1A'],
    emptyNodeColor : '#FFFFFF',
};

var mindGraph = {
    createNetwork : function (inputGraphData, networkElementId, nodeInfoElementId) {

        var clusters = inputGraphData.repr;
        var graph_data = {
            nodes: [],
            edges: []
        };
        var COLORS = mindGraphConstants.colors;
        var seen_nodes = {};
        for (i_cluster in clusters) {
            var data = clusters[i_cluster];
            var color = COLORS[i_cluster % COLORS.length];
            for (node in data.nodes) {
                if (!seen_nodes[node]) {
                    var node_attrs = data.nodes[node];
                    var label = node_attrs.text || node;

                    // Node without additional information is white
                    var node_color = mindGraphConstants.emptyNodeColor;

                    if (node_attrs.url || node_attrs.note) {
                        node_color = color;
                    }
                    var node_obj = {
                        'id': node,
                        'label': label,
                        'shape': 'box',
                        'color': node_color,
                        'mass': 2
                    };
                    if (data.nodes[node]['is_root']) {
                        node_obj.mass *= 2;
                        node_obj.font = {'size': 20};
                    }
                    graph_data.nodes.push(node_obj);
                    seen_nodes[node] = node_attrs;
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
        var container = document.getElementById(networkElementId);
        var options = {};
        var network = new vis.Network(container, graph_data, options);

        network.on("selectNode", function(params) {
            var node = params.nodes[0];
            var attrs = seen_nodes[node];

            var urls_html = "";
            for (i_html in attrs.url) {
                var url = attrs.url[i_html];
                urls_html += "<a href="+url+">"+url+"</a><p>";
            }

            var note_html = "";
            for (i_note in attrs.note) {
                var note = attrs.note[i_note];
                note_html += note + "<p>";
            }
            document.getElementById(nodeInfoElementId).innerHTML = "<h4>'"+node+"' info:</h4>" + urls_html + "<p>" + note_html;
        });
        return true;
    }
};