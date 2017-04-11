import re
from collections import defaultdict
from itertools import product
import networkx as nx


class Parser:
    COLORS = ['blue', 'green', 'red']
    spaces = re.compile(r'\s+')
    groups = re.compile(r'^(.+)\s+\.(\S+)\s+(.+)$')
    enumerations = re.compile(r'\s*,\s*')

    def parse_relations(self, text):
        relations = []
        for line in text.split('\n'):
            # cleanup
            line = line.strip()
            if not len(line) or line.startswith('#'):
                continue
            line = self.spaces.sub(' ', line)

            # parse
            m = self.groups.search(line)
            if m:
                f, r, t = m.group(1,2,3)
                for (fi, ti) in product(self.enumerations.split(f), self.enumerations.split(t)):
                    relations.append((fi, r, ti))
        return relations

    def make_graphs(self, relations):
        rgraphs = defaultdict(nx.Graph)
        for f, r, t in relations:
            rgraphs[r].add_edge(f, t, relation=r)
        return rgraphs

    def make_dot(self, rgraphs):
        rel_edges = []  # (relation, edges), (relation, edges), ...
        for relation, graph in rgraphs.items():
            for component in nx.connected_components(graph):
                subgraph = graph.subgraph(component)
                edges = subgraph.edges()

                edge_reprs = []
                for edge in edges:
                    color = self.COLORS[hash(relation) % len(self.COLORS)]
                    attributes = {'color': color}

                    if relation.startswith('is'):
                        attributes['dir'] = 'none'
                    edge_reprs.append(self._arc_repr(edge[0], edge[1], attributes))
                rel_edges.append([relation, edge_reprs])

        return self._rel_edges_to_dot(rel_edges)

    def parse_to_dot(self, text):
        relations = self.parse_relations(text)
        rgraphs = self.make_graphs(relations)
        return self.make_dot(rgraphs)

    def _arc_repr(self, v1, v2, attributes=None):
        qv1 = self._quote(v1)
        qv2 = self._quote(v2)
        if attributes is None:
            return "{} -> {}".format(qv1, qv2)
        else:
            attributes_repr = ",".join([str(k) + '=' + str(v) for k, v in attributes.items()])
            return "{} -> {} [{}]".format(qv1, qv2, attributes_repr)

    def _rel_edges_to_dot(self, rel_edges):
        # 'is' relations separated to subgraphs
        free_edges = []
        cluster_edges = dict()
        i=0
        for relation, edges in rel_edges:
            if relation.startswith('is'):
                cluster_edges[relation+str(i)] = edges[:]
                i += 1
            else:
                free_edges += edges
        cluster_reprs = [" subgraph cluster_"+relation + " {\n" + ";\n".join(edges) + "}\n" for relation, edges in cluster_edges.items()]
        return "digraph G { " + "\n".join(cluster_reprs) + ";\n".join(free_edges) + " }"

    def _quote(self, text):
        return '"{}"'.format(text)