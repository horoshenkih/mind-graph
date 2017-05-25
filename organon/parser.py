import re
from collections import defaultdict
from itertools import product
import networkx as nx
from bs4 import BeautifulSoup
from markdown import markdown
from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor


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


class MindGraphNodeVisitor(NodeVisitor):
    def generic_visit(self, node, visited_children):
        visited_children = list(filter(lambda x: x is not None, visited_children))
        if not visited_children:
            return
        elif len(visited_children) == 1:
            return visited_children[0]
        else:
            return visited_children

    def visit_endl(self, node, visited_children):
        return

    def visit_comment(self, node, visited_children):
        return {'type': 'comment', 'text': node.text}

    def visit_word(self, node, visited_children):
        return node.text

    def visit_node_id(self, node, visited_children):
        return node.text

    def visit_markdown(self, node, visited_children):
        rbrace, md, lbrace = visited_children
        if md is not None:
            return md.text

    def visit_any_text(self, node, visited_children):
        return node

    def visit_node(self, node, visited_children):
        node_id, _, md = visited_children
        rv = {'type': 'node_id', 'id': node_id}
        if md is not None:
            rv['markdown'] = md
        return rv

    def visit_node_enumeration(self, node, visited_children):
        c1, c2 = visited_children
        if c2 is None:
            c2 = []
        if isinstance(c2, str):
            c2 = [c2]
        return [c1]+c2

    def visit_relation(self, node, visited_children):
        from_nodes, _, _, relation, _, to_nodes = visited_children
        if isinstance(from_nodes, str):
            from_nodes = [from_nodes]
        if isinstance(to_nodes, str):
            to_nodes = [to_nodes]

        return {'type': 'relation', 'relation': [from_nodes, relation, to_nodes]}

    def visit_mind_graph(self, node, visited_children):
        return visited_children


class Parser:
    _grammar = r'''
        mind_graph          = ((_/endl)* (relation / node / comment) (_/endl)*)*

        relation_begin      = '.'
        node_enum_sep       = ','
        endl                = '\n'
        comment_start       = '#'
        _                   = ' ' / '\t'

        comment             = comment_start~"[^\n]+"
        #comment             = comment_start!endl*  # TODO!

        markdown            = ('{' (_/endl)*) any_text ((_/endl)* '}')
        any_text            = ~"[^{}]*"

        word                = ~"[^ #.,\t\n{}]+"
        #word                = !(comment_start / _ / endl / relation_begin / node_enum_sep / '{' / '}')+  # TODO!

        node_id             = word (_+ word)*
        node                = node_id (_/endl)* markdown?
        node_enumeration    = node_id (node_enum_sep _* node_id)*

        relation            = node_enumeration _+ '.'word _+ node_enumeration
    '''

    def __init__(self):
        self.grammar_parser = Grammar(self.grammar)
        self.node_visitor = MindGraphNodeVisitor()

    @property
    def grammar(self):
        return self._grammar

    def parse(self, text):
        parsed = self.grammar_parser.parse(text)
        return self.node_visitor.visit(parsed)

    def parse_relations(self, text):
        '''Transform text to RelationGraph.

        :param text:
        :return: RelationGraph object
        '''
        try:
            parsed = self.parse(text)
        except:
            raise RuntimeError("Cannot parse!")

        node_items = filter(lambda item: item.get('type') == 'node_id', parsed)
        node_attributes = dict()
        for item in node_items:
            node = item['id']
            node_html = markdown(item.get('markdown', ''), extensions=['urlize'])
            node_attributes[node] = {'html': node_html}
            parsed_html = BeautifulSoup(node_html, 'html.parser')
            if parsed_html.h1:
                node_attributes[node]['text'] = parsed_html.h1.string

        relation_items = filter(lambda item: item.get('type') == 'relation', parsed)
        relations = RelationGraph()
        for item in relation_items:
            f, r, t = item['relation']
            for (fi, ti) in product(f, t):
                edge_attributes = {}  # TODO!
                relations.add_relation(
                    Node(fi, node_attributes.get(fi)),
                    r,
                    Node(ti, node_attributes.get(ti)),
                    edge_attributes
                )

        return relations

    def parse_to_list(self, text):
        relations = self.parse_relations(text)
        return relations.represent()

    def parse_to_dot(self, text, clusters=True):
        relations = self.parse_relations(text)
        return relations.make_dot(clusters)