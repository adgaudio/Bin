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
from ds_commons import argparse_tools as at
from ds_commons.log import log


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


def main(ns):
    if ns.parallel:
        client = parallel.Client()
        pool = client.load_balanced_view()
        imap = pool.imap
        with client[:].sync_imports():
            from import_dag import get_related_fps
    else:
        imap = map
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

    #ns.draw(g)
    ##print g.connected_components


build_arg_parser = at.build_arg_parser([
    at.add_argument('-d', '--startdir', type=str, default='.'),
    at.add_argument('-p', '--parallel', action='store_true'),
    at.limit,
])


if __name__ == '__main__':
    NS = build_arg_parser().parse_args()
    g, glocal = main(NS)


"""
def to_module_str(fp):
    return basename(fp).rsplit('.')[0]


def get_modules(module):
    modules = set()
    if not type(module) in [types.ModuleType]:
        raise Exception('get_modules(module) must receive a types.ModuleType.'
                        '  Got %s' % type(module))
    for val in module.__dict__.values():
        _try_add_module(val, modules)
    return modules


def _try_get_attr(val, *attrs):
    rv = val
    for attr in attrs:
        if isinstance(attr, tuple):
            rv = _try_get_attr(rv, *attr)
        else:
            try:
                rv = getattr(rv, attr, None)
            except Exception as err:
                rv = None
                log.warning('getattr failed for %s. Error: %s'
                            % (attrs, err))

    if rv is not None and not (type(rv) in [str, types.ModuleType]):
        raise Exception("wrong type for %s. wtf?" % attr)
    return rv


def _try_add_module(val, modules):
    if isinstance(val, types.ModuleType):
        for attr in ['__package__', '__module__']:
            vv = _try_get_attr(val, attr)
            vv and modules.add(vv)
        if val.__package__ and val.__package__ not in val.__name__:
            vv = "%s.%s" % (val.__package__, val.__name__)
        else:
            vv = val.__name__
        modules.add(vv)
    else:
        for attr in ['__module__', ('__class__', '__module__')]:
            vv = _try_get_attr(val, attr)
            vv and modules.add(vv)
        if hasattr(val, '__package'):
            raise Exception("non package has __package?!")


def recursively_populate_lookup(module, lookup):
    # Import the module if it's not already loaded
    try:
        module = importlib.import_module(module)
    except:
        log.warn("Couldn't load module: %s" % module)
        raise

    try:
        return lookup[module]
    except KeyError:
        pass

    mods = get_modules(module)
    for mod in mods:
        recursively_populate_lookup(mod, lookup)

"""
