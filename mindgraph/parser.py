import re
from collections import defaultdict
from itertools import product
import networkx as nx


class Node:
    def __init__(self, name=None, attributes=None):
        self._name = name
        self._attributes = attributes

    @property
    def name(self):
        return self._name

    @property
    def attributes(self):
        return self._attributes


class RelationGraph:
    COLORS = ['blue', 'green', 'red']

    def __init__(self):
        self._rgraphs = defaultdict(nx.Graph)  # {relation_name: rgaph}
        self._nodes = dict()  # {name: attributes}

    def add_relation(self, node1, relation, node2):
        # for each node set first set of not None attributes
        for n in (node1, node2):
            if self._nodes.get(n.name) is None:
                if n.attributes is not None:
                    self._nodes[n.name] = n.attributes
                else:
                    self._nodes[n.name] = None
            elif n.attributes is not None:
                self._nodes[n.name].update(n.attributes)

        self._rgraphs[relation].add_edge(node1.name, node2.name, relation=relation)

    def get_relations(self, name1, name2):
        all_relations = []

        for r, rgraph in self._rgraphs.items():
            if rgraph.has_edge(name1, name2):
                all_relations.append(r)

        return set(all_relations)

    def get_nodes(self):
        return self._nodes.keys()

    def get_node_attribute(self, nodename, attrname):
        attrs = self._nodes.get(nodename)
        if attrs is None:
            return None
        elif type(attrs) == dict:
            return attrs.get(attrname)
        else:
            raise RuntimeError("Wrong type of attributes of node {}".format(nodename))

    def make_dot(self, clusters=True):
        rel_edges = []  # (relation, edges), (relation, edges), ...
        for relation, graph in self._rgraphs.items():
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

        return self._rel_edges_to_dot(rel_edges, clusters)

    def _quote(self, text):
        return '"{}"'.format(text)

    def _arc_repr(self, v1, v2, attributes=None):
        qv1 = self._quote(v1)
        qv2 = self._quote(v2)
        if attributes is None:
            return "{} -> {}".format(qv1, qv2)
        else:
            attributes_repr = ",".join([str(k) + '=' + str(v) for k, v in attributes.items()])
            return "{} -> {} [{}]".format(qv1, qv2, attributes_repr)

    def _rel_edges_to_dot(self, rel_edges, clusters=True):
        # 'is' relations separated to subgraphs
        free_edges = []
        cluster_edges = dict()
        i=0
        for relation, edges in rel_edges:
            if relation.startswith('is') and clusters:
                cluster_edges[relation+str(i)] = edges[:]
                i += 1
            else:
                free_edges += edges
        cluster_reprs = [" subgraph cluster_"+relation + " {\n" + ";\n".join(edges) + "}\n" for relation, edges in cluster_edges.items()]
        return "digraph G { " + "\n".join(cluster_reprs) + ";\n".join(free_edges) + " }"


class Parser:
    spaces = re.compile(r'\s+')
    groups = re.compile(r'''
        ^
        (.+)        # first vertex
        \s+
        \.(\S+)     # relation (single word starting with dot)
        \s+
        (.+)        # second vertex
        $
        ''', re.X)
    enumerations = re.compile(r'\s*,\s*')

    vertex_with_attributes = re.compile(r'''
        ^
        ([^\[\]]+?)         # vertex
        \s*
        (\[[^\[\]]+\])?     # optional attributes in square brackets
        $
    ''', re.X)

    attributes_split = re.compile(r'\s*;\s*')
    one_attribute_split = re.compile(r'\s*=\s*')

    def __init__(self, unique_attributes=['text'], multiple_attributes = ['tag', 'url', 'note']):
        self._unique_attributes = set(unique_attributes)
        self._multiple_attributes = set(multiple_attributes)
        if not self._unique_attributes.isdisjoint(self._multiple_attributes):
            raise ValueError("Sets with unique and multiple attributes must not overlap")

    def _parse_attributes(self, attributes_text):
        if attributes_text is None:
            return None
        attributes_text = re.sub(r'^\[|\]$', repl='', string=attributes_text)

        attributes = dict()
        for kv in self.attributes_split.split(attributes_text):
            k, v = self.one_attribute_split.split(kv, maxsplit=1)
            if k in self._unique_attributes:
                attributes[k] = v
            elif k in self._multiple_attributes:
                if k in attributes:
                    attributes[k].append(v)
                else:
                    attributes[k] = [v,]
        return attributes

    def parse_relations(self, text):
        '''Transform text to RelationGraph.

        :param text:
        :return: RelationGraph object
        '''
        relations = RelationGraph()

        for i, rawline in enumerate(text.split('\n')):
            # cleanup
            line = rawline.strip()
            if not len(line) or line.startswith('#'):
                continue
            line = self.spaces.sub(' ', line)

            # parse
            m = self.groups.search(line)
            if m:
                f, r, t = m.group(1,2,3)
                for (fi, ti) in product(self.enumerations.split(f), self.enumerations.split(t)):
                    fi, attr_fi_str = self.vertex_with_attributes.search(fi).group(1,2)
                    ti, attr_ti_str = self.vertex_with_attributes.search(ti).group(1,2)
                    attr_fi = self._parse_attributes(attr_fi_str)
                    attr_ti = self._parse_attributes(attr_ti_str)
                    relations.add_relation(Node(fi, attr_fi), r, Node(ti, attr_ti))
            else:
                raise RuntimeError("Incorrect line {}: '{}'".format(i+1, rawline))

        return relations

    def parse_to_dot(self, text, clusters=True):
        relations = self.parse_relations(text)
        return relations.make_dot(clusters)