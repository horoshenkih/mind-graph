from argparse import ArgumentParser
from subprocess import Popen
import os
import sys
import signal
import time
from tempfile import NamedTemporaryFile
import json

BASE_PATH = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))
sys.path.append(BASE_PATH)

from organon.parser import Parser

TEMPLATE = """
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">

    <title>MindGraph</title>

    <link rel="stylesheet" href="file://{css_path}/common.css">
    <script src="//ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>
    <script src="file://{js_path}/third-party/vis.min.js"></script>
    <script src="file://{js_path}/lib/mindgraph.js"></script>
</head>

<body>
    <div class="row">
        <div id="nodeInfo" class="col-sm-3"></div>
        <div id="network" class="col-sm-9"></div>
        <script>
            var graphData = {graph_json};
            var graph = MindGraph.init(graphData);
            var network = graph.createNetwork('network', 'nodeInfo');
        </script>
    </div>
</body>
"""

class TemporaryPage:
    def __init__(self, html, browser='firefox'):
        f = NamedTemporaryFile(suffix='.html', mode='w')
        f.write(html)
        f.flush()
        self._page = f
        self._pid = Popen([browser, f.name]).pid

    def cleanup(self):
        self._page.close()
        os.kill(self._pid, signal.SIGTERM)


if __name__ == '__main__':
    try:
        parser = ArgumentParser()
        parser.add_argument('mindgraphs', nargs='+')
        parser.add_argument('-b', '--browser', default='google-chrome')
        args = parser.parse_args()

        # read mindgraphs
        mindgraph_contents = []
        for mg in args.mindgraphs:
            with open(mg) as mgf:
                mindgraph_contents.append(mgf.read())

        # parse
        ps = Parser()
        parsed_json = json.dumps(ps.parse_to_list('\n'.join(mindgraph_contents)))

        # draw
        html = TEMPLATE.format(
            js_path=os.path.join(BASE_PATH, 'static', 'js'),
            css_path=os.path.join(BASE_PATH, 'static', 'css'),
            graph_json=parsed_json
        )
        t = TemporaryPage(html, browser=args.browser)
        while True:
            time.sleep(1000)
    except KeyboardInterrupt:
        t.cleanup()
