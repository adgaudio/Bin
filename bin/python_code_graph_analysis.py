"""
Analyze how python code is structured
by examining which modules import each other

Put the data into a graph structure.
  - if your modules aren't a DAG (directed acyclic graph), meaning two modules
  import each other, your code should be fixed!
  - examine most highly connected components to know what are key files in a
  repo
  - plot code structure as a tree for teaching others how your code works
  - etc
"""
import networkx as nx
import re
import os
import modulefinder
from os.path import join, abspath
from IPython import parallel
import argparse as at
import logging as log


def build_graph(lookup):
    g = nx.DiGraph()
    g.add_edges_from((n1, n2)
                     for n1 in lookup for n2 in lookup[n1]
                     if n2 is not None and n1 is not None)
    return g


def vis_graph(graph):
    pass


def is_dag(graph):
    """Does graph have any cycles?"""
    pass


def get_related_fps(fp):
    log.info('Finding modules for: %s' % fp)
    f = modulefinder.ModuleFinder()
    try:
        f.run_script(fp)
    except ImportError as err:
        log.warn(err)
        return []

    return [abspath(mod.__file__ or mod.__path__)
            for mod in f.modules.values()
            if mod.__file__ or mod.__path__]


def get_map_func(use_parallel):
    if use_parallel:
        client = parallel.Client()
        pool = client.load_balanced_view()
        imap = pool.imap

        def engine_imports():
            from __file__ import get_related_fps, log
            get_related_fps, log
        client[:].apply(engine_imports)
    else:
        imap = map
    return imap


def main(ns):
    imap = get_map_func(ns.parallel)
    fps = [abspath(join(cwd, fp))
           for cwd, __, fps in os.walk(ns.startdir)
           for fp in fps
           if re.match('.*\.py[x]?$', join(cwd, fp))
           ]

    if ns.limit:
        fps = fps[:ns.limit]

    log.info('finding related modules')
    lookup = {}  # {module1: [other imported modules]}
    for fp, related_fps in zip(fps, list(imap(get_related_fps, fps))):
        if related_fps:
            lookup[fp] = [abspath(x) for x in related_fps]

    log.info('build graph')
    g = build_graph(lookup)
    assert g.size()
    glocal = g.subgraph(x for x in g.nodes()
                        if x.startswith(abspath(ns.startdir)))
    return g, glocal


def build_arg_parser():
    p = at.ArgumentParser()
    p.add_argument('-d', '--startdir', type=str, default='.'),
    p.add_argument('-p', '--parallel', action='store_true',
                   help='Use IPython.parallel and assume an ipcluster is'
                   'running on localhost'),
    p.add_argument('-l', '--limit', default=0, type=int)
    return p


if __name__ == '__main__':
    NS = build_arg_parser().parse_args()
    g, glocal = main(NS)
