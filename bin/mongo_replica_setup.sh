wget -O /tmp/simple-setup.py -nc raw.github.com/mongodb/mongo-snippets/master/replication/simple-setup.py
mkdir -p /tmp/db/replset
python /tmp/simple-setup.py --mongo_path $(dirname $(which mongod)) --dbpath /tmp/db/replset $@

