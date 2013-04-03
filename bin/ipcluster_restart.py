"""
There are better options available for ipython.

So you shouldn't use this. (Checkout StarCluster's ipython plugin, for instance)

I'm publishing this to my git repo for reference rather than usability.

---

Tools to handle starting and stopping IPython 0.13 ipcontrollers and ipengines.
Basically, this code wraps ipython's toolset because ipython wasn't always
performing the way the docs said it was.  This ensures that engines die
the way you'd expect (hard or soft kill), pids are always removed appropriately,
etc.

Does not manage json files, unless used in conjunction with fabric like below:
    (you would probably need to tweak the fabric code to fit your usecase)

---


import fabric.api as f
import functools
from os.path import basename, dirname, join, exists
import random
import redis
from time import sleep

from mycode import ssh_tunnel, config_base


def _srun():
    user = f.env.sudo_user
    srun = functools.partial(f.sudo, user=user)
    functools.update_wrapper(srun, f.sudo)
    return srun


@ds_shared.cached  # TODO: hopefully this wont cache the tmux session initialization across hosts.
def _srun_tmux_setup(session_name=None):
    if not session_name:
        session_name = f.env.tmux_session_name
    srun = _srun()
    srun(("tmux has-session -t {session_name} || tmux new-session -d -s"
          " {session_name} 'sleep 100'"
          ).format(session_name=session_name))


def _srun_tmux(window_name=None, session_name=None):
    "Return srun() function who's shell is set to run inside a tmux session
    and in background
    Optionally set tmux window name, but remember that you can't run two
    processes simultaneously in the same window"
    srun = _srun()
    _srun_tmux_setup(session_name)
    if not session_name:
        session_name = f.env.tmux_session_name
    shell = '%s new-window -d -t %s' % (f.env.tmux_shell, session_name)
    if window_name:
        shell += ' -n %s' % window_name
    return f.with_settings(shell=shell)(srun)


@f.roles('proc_controller')
def _ipcontroller_start(cluster_id, json_dir):
    srun_tmux = _srun_tmux(window_name=('ipcontroller_%s' % cluster_id))
    srun = _srun()
    # TODO: implement a get_static(files=()), or the reverse of deploy_static()
    ipcluster_restart.start_ipcontroller(cluster_id, srun, srun_tmux)
    targz = '/tmp/json_files.tar.gz'
    srun('tar cvzf {targz} {json_dir}; chmod -R 777 {targz}'.format(
        targz=targz, json_dir=json_dir))
    f.get(remote_path=targz, local_path="%s_1" % targz)
    f.local('(cd / ; tar xvzf {targz}_1)'.format(
        json_dir=json_dir, targz=targz))


@f.roles('proc_controller')
def _ipcontroller_stop(excludes):
    srun = _srun()
    ipcluster_restart.kill_ipcontrollers(
        excludes, srun, f.env.client_sshserver)


@f.parallel
@f.roles('proc')
def _ipengine_start(cluster_id, json_path):
    tmp_path = '/tmp/%s' % basename(json_path)
    # TODO: use deploy_static
    srun = _srun()
    f.put(local_path=json_path, remote_path=tmp_path)
    srun('cp {tmp} {json} ; rm -f {tmp}'.format(tmp=tmp_path, json=json_path))
    srun_tmux = _srun_tmux('ipengine_%s' % cluster_id)
    ipcluster_restart.start_ipengines(cluster_id, srun_tmux)


@f.parallel
@f.roles('proc')
def _ipengine_stop(excludes):
    srun = _srun()
    ipcluster_restart.kill_ipengines(excludes, srun)


@f.roles('proc_controller')
def _find_active_clusters(excludes):
    srun = _srun()
    return ipcluster_restart.find_clusters_with_outstanding_jobs(
        excludes, srun, f.env.client_sshserver)


@f.roles('redis_server')
def _redis_update_cluster_id(cluster_id):
    print f.env.redis_env
    client = redis.StrictRedis(**f.env.redis_env)
    with client.pipeline() as pipe:
        pipe.lpush(config_base.REDIS_CLUSTER_ID_KEY, cluster_id)
        pipe.ltrim(config_base.REDIS_CLUSTER_ID_KEY, 0, 19)
        pipe.execute()


def ipy_restart(cluster_id):
    json_path = config_base.IPY_JSON_FPATH.format(cluster_id=cluster_id)
    # Start ipcontroller and ipengines
    f.execute(_ipcontroller_start, cluster_id, dirname(json_path))
    f.execute(_ipengine_start, cluster_id, json_path)
    f.execute(_redis_update_cluster_id, cluster_id)

    # TODO: verify engines started!!!

    # Gracefully Stop old ipcontrollers and ipengines
    excludes = [cluster_id]
    f.execute(_ipcontroller_stop, excludes=excludes)
    sleep(4)
    [excludes.extend(cids)
     for cids in f.execute(_find_active_clusters, excludes).values()]
    f.execute(_ipengine_stop, excludes=excludes)
"""

import IPython.parallel as parallel
import gevent
import os
import shlex
import subprocess
import time

from mycode import config_base


def local(cmd):
    print cmd
    proc = subprocess.Popen(shlex.split(cmd),  # shell=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return proc.communicate()[1]


def kill_cluster(client, cluster_id, popen):
    print cluster_id
    client.spin()  # updates client cache
    _status = client.queue_status()
    ntasks = (_status.pop('unassigned')
              + sum(eng['queue'] for eng in _status.values())
              + sum(eng['tasks'] for eng in _status.values()))
    if client.outstanding or ntasks:
        if not client.ids:
            raise parallel.error.NoEnginesRegistered(
                'No engines registered AND there are outstanding or'
                ' unfinished tasks. cluster_id: %s' % cluster_id)
        print ("Controller busy crunching {num} outstanding tasks.  Not killing"
               ).format(num=ntasks)
        return

    client.wait()
    try:
        client.shutdown(hub=True)
    except parallel.error.NoEnginesRegistered, e:
        print "Killing ipcontroller with 0 engines and 0 outstanding jobs: %s" % cluster_id
        cmd = ("ps -eo user,pid,command | grep -v ^root | grep ipcontroller "
               " | grep 'profile={profile_name}' | grep cluster-id={cluster_id}"
               " | grep -v grep | tr -s ' ' ' ' | cut -d\  -f2"
               " | xargs --no-run-if-empty kill").format(
                   profile_name=config_base.IPY_PROFILE_NAME,
                   cluster_id=cluster_id)
        popen(cmd)


def find_ipcontroller_pid_files(popen):
    """Popen must be able to capture stdout"""
    pid_file_dir = os.path.dirname(config_base.IPY_PID_FPATH)
    fname = os.path.basename(config_base.IPY_PID_FPATH.format(cluster_id='*'))
    cmd = 'find {} -name {}'.format(pid_file_dir, fname)
    pid_files = popen(cmd).split()
    return [fp for fp in pid_files
            if fp.endswith('.pid') and 'ipcontroller-' in fp]


def get_clients_from_pid_files(pid_files, excludes=(), client_sshserver=None,
                               _clients={}):
    cluster_ids = [pf.split('-')[-1].split('.')[0]
                   for pf in pid_files]
    cluster_ids = [cid for cid in cluster_ids if cid not in excludes]
    json_fnames = [(cid, config_base.IPY_JSON_FNAME.format(cluster_id=cid))
                   for cid in cluster_ids]
    for cid, json_fname in json_fnames:
        if cid not in _clients:
            connect_client = lambda: parallel.Client(
                json_fname,
                profile=config_base.IPY_PROFILE_NAME,
                sshserver=client_sshserver,
                ipython_dir=os.path.dirname(config_base.IPY_PROFILE_DIR))
            try:
                _clients[cid] = connect_client()
            except:
                try:
                    _clients[cid] = connect_client()
                except parallel.error.TimeoutError:
                    print "WARNING! Can't connect to Hub at cluster_id: %s" % cid
    return {cid: client for cid, client in _clients.items() if cid in cluster_ids}


def find_clusters_with_outstanding_jobs(excludes, popen, client_sshserver=None):
    pid_files = find_ipcontroller_pid_files(popen)
    clients = get_clients_from_pid_files(pid_files,
                                         client_sshserver=client_sshserver)

    has_tasks = lambda qstatus: (qstatus.pop('unassigned')
              + sum(eng['queue'] for eng in qstatus.values())
              + sum(eng['tasks'] for eng in qstatus.values()))
    return [cid for cid, client in clients.items()
            if client.outstanding or has_tasks(client.queue_status())]


def kill_ipcontrollers(excludes, popen, client_sshserver=None):
    """Find all running ipcontrollers and kill them unless
    the cluster-id is in the excudes list.
    popen must be able to capture stdout"""
    pid_files = find_ipcontroller_pid_files(popen)
    clients = get_clients_from_pid_files(pid_files, excludes=excludes,
                                         client_sshserver=client_sshserver)
    kill_jobs = [gevent.spawn(kill_cluster, client, cluster_id, popen)
                 for cluster_id, client in clients.items()]
    [j.link_exception() for j in kill_jobs]
    gevent.joinall(kill_jobs)


def kill_ipengines(excludes, popen):
    """Kill all unecessary engines lying around
    Dont kill cluster_ids in the excludes list"""
    if excludes:
        grep_excludes = " | grep -vE '({})'".format(
            '|'.join('cluster-id=%s' % cid for cid in excludes))
    else:
        grep_excludes = ''
    cmd = ("ps -eo user,pid,command | grep -v ^root | grep ipengine "
           " | grep 'profile={profile_name}' {grep_excludes} | grep -v grep"
           " | tr -s ' ' ' ' | cut -d\  -f2 | xargs --no-run-if-empty kill"
           ).format(
               profile_name=config_base.IPY_PROFILE_NAME,
               grep_excludes=grep_excludes)
    popen(cmd)


def start_ipcontroller(cluster_id, popen, popen_daemon, sleep=1):
    """Start ipython ipcontroller with a trap that kills the pid file on exit.
    `popen` must capture and return stdout.  `popen_daemon` should
    background the given bash cmd, or it will block until process dies.
    Verify ipcontroller is running `sleep` seconds after executing"""
    # Build bash cmd
    cmd = ('IPYTHONDIR={profile_dir} ipcontroller'
           ' --profile={profile_name} --cluster-id={cluster_id}'
           ' --ip={host_addr} --log-to-file --profile-dir={profile_dir}'
           ' --work-dir={repo_path} --dictdb').format(
               profile_name=config_base.IPY_PROFILE_NAME,
               cluster_id=cluster_id,
               #host_addr=r"$(host $(hostname) | awk '{print $4}')")
               host_addr='*',
               profile_dir=config_base.IPY_PROFILE_DIR,
               repo_path=config_base.DATASCIENCE_REPO_PATH)
    pid_file = config_base.IPY_PID_FPATH.format(cluster_id=cluster_id)
    json_path = config_base.IPY_JSON_FPATH.format(cluster_id=cluster_id)
    jp2 = json_path.replace('engine.json', 'client.json')
    trapped_cmd = ("""/bin/bash -c "trap 'rm {pid_file} {json_path} {jp2}' EXIT"""
                   """ ; {cmd}" """).format(**locals())
    # Verify this cluster is not already running
    if not (all(cluster_id not in os.path.basename(fp)
            for fp in find_ipcontroller_pid_files(popen))):
        raise parallel.error.ControllerCreationError(
            'ipcontroller already running or pid file was never removed')
    # Start ipcontroller and verify it started
    popen_daemon(trapped_cmd)
    time.sleep(sleep)
    if not (any(cluster_id in os.path.basename(fp)
            for fp in find_ipcontroller_pid_files(popen))):
        raise parallel.error.ControllerCreationError(
            'ipcontroller failed to start')


def start_ipengines(cluster_id, popen):
    cmd = ('IPYTHONDIR={profile_dir} ipengine'
           ' --profile={profile_name} --cluster-id={cluster_id}'
           ' --profile-dir={profile_dir} --work-dir={repo_path}'
           ' --log-to-file ').format(
               profile_name=config_base.IPY_PROFILE_NAME,
               cluster_id=cluster_id,
               profile_dir=config_base.IPY_PROFILE_DIR,
               repo_path=config_base.DATASCIENCE_REPO_PATH)
    [popen(cmd) for _ in range(config_base.IPY_NUM_PROCS_PER_NODE)]
