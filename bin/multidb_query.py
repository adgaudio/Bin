#!/usr/bin/env python
""" Remotely execute query on multiple databases. Drop into ipython shell for data exploration
TODO: make run comparison on stage and prod agnostic of which machine it's on"""
import sys
from utils import opendb
from IPython import embed

def run(query, dbs, keep_alive=False, stdout=False):
  """given sql query as string, and sequence of db connections,
  execute given query on given dbs and return results
  """
  queries = [x.strip() for x in query.strip().split(';') if x != '']

  try:
    conns, curs = [], []
    for d in dbs:
      conn, cur = opendb(*d)
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

  if stdout:
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

def testrow(querydata):
    """Given result data from a specific query
    (ie data[0] or something in form: {db1: ((row1,), (row2,), ...), db2:...} ),
    return rows that aren't equal
    """

    unequaldata = {}
    for c,tup in enumerate(zip(*querydata.values())):
        if not all(row == tup[0] for row in tup[1:]):
            unequaldata[c] = tup
    return unequaldata
    # another way of doing the same thing.
    return [tup for c,tup in enumerate(zip(*querydata.values())) if not all(row == tup[0] for row in tup[1:])]

def testcolumn(querydata, rownumber):
    """Find columns that aren't equal for given row
       Return dict of {column_index:[db1column_value, db2column_value, ...], ...}

    querydata in form: {db1:((row1col1, row1col2, ...), ...), ...}
    Return columns per row that aren't equal in form:
        {col_index1:(db1_col, db2_col)}
    """
    return {index:cols for index,cols in enumerate(zip(*zip(*querydata.values())[rownumber])) if not all(col == cols[0] for col in cols[1:])}

def testcolumns(querydata, rownums):
    """Given result data from specific query (ie data[5])
        and list of row numbers (ie testrow(data[5].keys()),
       Return cols that aren't same for every row, keyed by col index
    """
    return [testcolumn(querydata, x) for x in rownums]

def test(data):
    """For every query, test if data returned by run() is equal"""
    result = []
    for query in data.values():
        query_result = True
        qresults = query.values()
        for cursor_result in qresults[1:]:
           query_result = query_result and cursor_result == qresults[0] and True
        result.append(query_result)
    return [(c,x) for c,x in enumerate(result)]
    # another way of doing the same thing.
    return [(c,x) for c,x in enumerate(['Equal' if x else 'NOT EQUAL' for x in [cursor_result == query[0] for query in data.values() for cursor_result in query.values()[1:] ]   ])]

def getrow(querydata, rownum):
    return [querydata[db][rownum] for db in querydata]

def getrows(querydata, rownumbers):
    rows = {}
    for n in rownumbers:
        rows[n] = getrow(querydata, n)


if __name__ == '__main__':
  from settings import dbs
  try:
    QUERY = open(sys.argv[1], 'r').read()
  except:
    print 'from query import QUERY FAILED.  using default query.sql'
    QUERY = open('query.sql', 'r').read()

  data, queries, conns, curs = run(QUERY, dbs, keep_alive=True, stdout=True)
  testdata = lambda: test(data)
  queries = [(c,x) for c,x in enumerate(queries)]
  embed()
  [x.close() for x in conns]

