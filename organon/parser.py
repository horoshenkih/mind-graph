import re
from collections import defaultdict
from itertools import product
import networkx as nx
from bs4 import BeautifulSoup
from markdown import markdown


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
    def __init__(self):
        self._rgraphs = defaultdict(nx.DiGraph)  # {relation_name: rgaph}
        self._nodes = dict()  # {name: attributes}

    def add_relation(self, node1, relation, node2, attributes={}):
        # for each node set first set of not None attributes
        for n in (node1, node2):
            if self._nodes.get(n.name) is None:
                if n.attributes is not None:
                    self._nodes[n.name] = n.attributes
                else:
                    self._nodes[n.name] = None
            elif n.attributes is not None:
                self._nodes[n.name].update(n.attributes)

        self._rgraphs[relation].add_edge(node1.name, node2.name, relation=relation, **attributes)

    def get_relations(self, name1, name2):
        all_relations = []

        for r, rgraph in self._rgraphs.items():
            if rgraph.has_edge(name1, name2):
                all_relations.append(r)

        return set(all_relations)

    def get_nodes(self):
        return self._nodes.keys()

    def get_node_attributes(self, nodename):
        attrs = self._nodes.get(nodename)
        if attrs is None:
            return {}
        else:
            return attrs

    def get_node_attribute(self, nodename, attrname):
        attrs = self.get_node_attributes(nodename)
        if attrs is None:
            return None
        elif type(attrs) == dict:
            return attrs.get(attrname)
        else:
            raise RuntimeError("Wrong type of attributes of node {}".format(nodename))

    def represent(self, analyze_graph=True):
        '''Get representation of graph as list of dicts.
        Each dict has the following structure:
        {
            'attributes': {'relation': relation_name, attr1: val1, ...},
            'nodes': {node1: node_attrs1, node2: node_attrs2, ...}
            'edges': {{node1: {node12, edge_attrs1}, node13: edge_attrs2, ...}, ...}
        }
        If bool(['attributes']['is_directed']) == False, then nodes in each edge are sorted in lexicografic order.

        :return: list of dicts
        '''

        representation = []

        for relation, graph in self._rgraphs.items():
            undirected = nx.Graph()
            undirected.add_edges_from(graph.edges())
            for component in nx.connected_components(undirected):
                graph_dict = {'attributes': {'relation': relation}, 'nodes': dict(), 'edges': dict()}

                subgraph = graph.subgraph(component)
                is_tree = False
                if analyze_graph:
                    is_tree = nx.is_tree(subgraph)
                root_node = None
                if analyze_graph and is_tree:
                    root_node = [n for n, d in subgraph.out_degree().items() if d == 0][0]

                for node in component:
                    node_attrs = self.get_node_attributes(node)
                    if analyze_graph and is_tree and node == root_node:
                        node_attrs['is_root'] = True
                    graph_dict['nodes'][node] = node_attrs
                edges = subgraph.edges(data=True)  # with attributes

                for edge in edges:
                    v1, v2, attrs = edge
                    if is_tree:
                        attrs['layout'] = 'tree'
                    if v1 not in graph_dict['edges']:
                        graph_dict['edges'][v1] = {}
                    graph_dict['edges'][v1][v2] = attrs
                representation.append(graph_dict)

        return representation


class Parser:
    comment = re.compile(r'#[^\n]*')
    spaces = re.compile(r'\s+')
    groups = re.compile(r'''
        ^
        ([^\{\}]+)        # first vertex
        \s+
        \.(\S+)     # relation (single word starting with dot)
        \s+
        ([^\{\}]+)        # second vertex
        $
        ''', re.X)
    enumerations = re.compile(r'\s*,\s*')

    node_with_attributes = re.compile(r'''
        ^\s*
        ([^\n\{\}]+?)         # node
        \s*
        \{([^\{\}]+?)\}     # attributes in curly brackets
        \s*$
    ''', re.X | re.S | re.M)

    # https://gist.github.com/gruber/249502
    url_re = re.compile(r'(?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))')

    def parse_relations(self, text):
        '''Transform text to RelationGraph.

        :param text:
        :return: RelationGraph object
        '''
        relations = RelationGraph()

        # parse nodes markdown
        node_attributes = dict()
        for match_node_md in self.node_with_attributes.findall(text):
            node, md = match_node_md
            # substitute_url
            md = self.url_re.sub(r'[\1](\1)', md)
            node_html = markdown(md)
            node_attributes[node] = {'html': node_html}
            parsed = BeautifulSoup(node_html, 'html.parser')
            if parsed.h1:
                node_attributes[node]['text'] = parsed.h1.string
        text = self.node_with_attributes.sub('', text)

        # remove comments
        text = self.comment.sub('', text)

        # parse relations
        for i, rawline in enumerate(text.split('\n')):
            # cleanup
            line = rawline.strip()
            if not len(line):
                continue
            line = self.spaces.sub(' ', line)

            # parse
            m = self.groups.search(line)
            if m:
                f, r, t = m.group(1,2,3)
                for (fi, ti) in product(self.enumerations.split(f), self.enumerations.split(t)):
                    edge_attributes = {}  # TODO?
                    relations.add_relation(
                        Node(fi, node_attributes.get(fi)),
                        r,
                        Node(ti, node_attributes.get(ti)),
                        edge_attributes
                    )
            else:
                raise RuntimeError("Incorrect line {}: '{}'".format(i+1, rawline))

        return relations

    def parse_to_list(self, text):
        relations = self.parse_relations(text)
        return relations.represent()

    def parse_to_dot(self, text, clusters=True):
        relations = self.parse_relations(text)
        return relations.make_dot(clusters)