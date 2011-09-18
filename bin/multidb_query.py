#!/usr/bin/env python
""" Remotely execute query on multiple databases.
Drop into ipython shell for data exploration
"""
import sys
import MySQLdb
from IPython import embed

def run(query, dbs, keep_alive=False):
  """given sql query as string, and sequence of db connections
  in form (host, user, passwd, db),
  execute given query on given dbs and return results
  """
  queries = [x.strip() for x in query.strip().split(';') if x != '']

  try:
    # Open db connections
    conns, curs = [], []
    for d in dbs:
      conn = MySQLdb.connect(**d) # (host, user, passwd, db)
      cur = conn.cursor()
      conns.append(conn)
      curs.append(cur)

    data = {}
    # Execute queries and store result in form: data = { query1: {cursor1: result1, ...}, ...}
    for query_id, q in enumerate(queries):
      data[query_id] = {}
      # Execute given query on all cursors
      for c in curs:
        c.execute(q)
      # Fetch and store result from all cursors
      for cursor_id,c in enumerate(curs):
        data[query_id][cursor_id] = c.fetchall()
  finally:
    if not keep_alive:
      [x.close() for x in conns]

  print """
  Executed the following query on the following machines:

    Query
    ===
    %s
    ===

    Machines
    ===
    %s
    ===

  Query results are stored in the variable "data" and are numbered by semicolon.
  Type 'whos' to see your namespace.
  """ % ('\n    '.join(str(x) for x in queries), '\n    '.join(str(x) for x in dbs))

  if keep_alive:
    return data, queries, conns, curs
  else:
    return data, queries

def test(data):
      """For every query, test if data returned by run() is equal"""
#      result = []
#      for query in data.values():
#          query_result = True
#           qresults = query.values()
#          for cursor_result in qresults[1:]:
#              query_result = query_result and cursor_result == qresults[0] and True
#          result.append(query_result)
#      return result
      # another way of doing the same thing. above is broken?
      return [(c,x) for c,x in enumerate(['Equal' if x else 'NOT EQUAL' for x in [cursor_result == query.values()[0] for query in data.values() for cursor_result in query.values()[1:] ]   ])]

if __name__ == '__main__':

  try:
    QUERY = open(sys.argv[1], 'r').read()
  except:
    print 'No filepath in sys.argv.  Using default: query.sql'
    QUERY = open('query.sql', 'r').read()

  dbs = ({'host': 'localhost', 'user':'root', 'db':'drupal', 'unix_socket':'/tmp/mysql.sock'},
        { 'host': 'localhost', 'user':'root', 'db':'content_field', 'unix_socket':'/tmp/mysql.sock'})

  data, queries, conns, curs = run(QUERY, dbs, keep_alive=True)
  testdata = lambda: test(data)
  queries = [(c,x) for c,x in enumerate(queries)]
  embed()
  [x.close() for x in conns]

