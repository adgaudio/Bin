import pymongo


def get_db(dbname='t'):
    db = pymongo.Connection()[dbname]
    return db


def make_capped_collection(db, name='capped_aavenaoweaenvreaoiewoxovo',
                           options={'capped': True, 'size': 50, 'max': 5}):
    db.drop_collection(name)
    col = db.create_collection(name, **options)
    col.create_index([('cid', pymongo.ASCENDING)])
    return col


def insert(col):
    x = 0
    while 1:
        for _ in range(4):
            col.insert({'cid': 1, 'x': x})
            x += 1
        yield


def consumer(col):
    return col.find_and_modify(query=dict(cid=1),
                               sort={'$natural': 1},
                               update={'cid': None})

if __name__ == '__main__':
    db = get_db()
    col = make_capped_collection(db)
    inserter = insert(col)
    inserter.next()
    print 'created a capped collection:'
    print '\n'.join(str(x) for x in (col.find({})))
    print '\ninserting more elements than the collection can hold.  current collection state:'
    inserter.next()
    inserter.next()
    inserter.next()
    print '\n'.join(str(x) for x in (col.find({})))
    print '\nconsuming 2 elements:'
    print consumer(col)
    print consumer(col)
    print '\ncurrent state of the database'
    print '\n'.join(str(x) for x in (col.find({})))
