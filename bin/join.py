import csv
from os.path import basename
from collections import defaultdict


def maybe(f):
    def tryer(*args, **kwargs):
        try:
            f(*args, **kwargs)
        except Exception, e:
            print "%s:%s" % (e.__class__.__name__,  e)
            print "args: %s %s" % (args, kwargs)
            print 'oh well...'
            pass
    print 'hi'
    return tryer


def join_csv(filepath, filepath2, key, inner_join=False):
    """Merge contents of 2 csv files given a join key"""
    print """%s Join of: \"%s\" 
         with: \"%s\" 
           on:   \"%s\" """ % (
            "Inner" if inner_join else "Outer",
            basename(filepath),
            basename(filepath2), key)

    if inner_join:
        d = dict()
    else:
        d = defaultdict(dict)
    header = []

    reader = csv.DictReader(open(filepath, 'rb'))
    [header.append(x) for x in reader.fieldnames if x not in header]
    for line in reader:
        d[line[key]] = line

    reader = csv.DictReader(open(filepath2, 'rb'))
    [header.append(x) for x in reader.fieldnames if x not in header]
    for line in reader:
        try:
            d[line[key]].update(line)
        except:
            print "Did not join data: %s" % line

    return header, d.values()


def write_csv(filepath, header, data):
    print "Writing to %s" % basename(filepath)
    o = csv.DictWriter(open(filepath, 'w'), header)
    o.writeheader()
    o.writerows(data)


if __name__ == '__main__':
    import sys
    filepath = sys.argv[1]
    filepath2 = sys.argv[2]
    joinkey = sys.argv[3]
    fpout = sys.argv[4]
    write_csv(fpout, *join_csv(filepath, filepath2, joinkey))
