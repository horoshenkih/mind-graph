import re
from collections import defaultdict

def parse_to_dot(text):
    def quote(text):
        return '"{}"'.format(text)
    COLORS = ['blue', 'green', 'red']

    relations = defaultdict(list)

    spaces = re.compile(r'\s+')
    groups = re.compile(r'^(.+)\s+\.(\S+)\s+(.+)$')
    for line in text.split('\n'):
        # cleanup
        line = line.strip()
        if not len(line) or line.startswith('#'):
            continue
        line = spaces.sub(' ', line)
        
        # parse
        m = groups.search(line)
        if m:
            f, r, t = m.group(1,2,3)
            relations[r].append((f,t))

    edges_repr = []
    n_relations = len(relations)
    for i, r in enumerate(relations.items()):
        relation, edges = r
        color = COLORS[i % n_relations]
        attributes = {'color': color}
        if relation.startswith('is'):
            attributes['dir'] = 'none'
        attributes_repr = ",".join([str(k)+'='+str(v) for k,v in attributes.items()])

        for edge in edges:
            edges_repr.append("{} -> {} [{}]".format(
                quote(edge[0]),
                quote(edge[1]),
                attributes_repr)
            )
    return "digraph G { " + ";\n".join(edges_repr) + " }" 
