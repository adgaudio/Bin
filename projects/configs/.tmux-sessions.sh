
# Automatically create a new session with these windows

function try-attach 
{
    tmux has-session -t $1
    if [ "$?" -eq 0 ] ; then
        (tmux attach -t $1)
    else
        exit 1
    fi
}

function except 
{
    if [ "$?" -eq 1 ] ; then
        $1
    fi
}

function session-fwk 
{
    tmux new-session -d -s fwk
    
    new -d -s fwk
    neww -k -t fwk:1
    neww -k -t fwk:2 -n sreports -send-keys 'sreports'
    neww -k -t fwk:3 -n prod -send-keys 'reports'
    neww -k -t fwk:4 -n local
}

function session-daemons
{
    tmux new -d -s daemons
    neww -k -n manage -t daemons:1 
}

function session-hi
{
    tmux new -d -s 'hi!'
    tmux neww -k -t hi!:1
}

for x in "hi fwk daemons" ; do
    try-attach $x
    except session-$x
done

link-window -dk -s daemons:manage -t hi:0