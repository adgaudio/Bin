# Automatically create a new session with these windows

#Register sessions that will be created by this script
SESSIONS="fwk hi daemons"

function has-session {
    tmux has-session -t $1 2>/dev/null
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
    tmux neww -k -t fwk:1
    tmux neww -k -n sreports -t fwk:2 
    tmux neww -k -n prod  -t fwk:3 
    tmux neww -k -n local -t fwk:4 
    
    tmux send-keys -t fwk:2 'sreports'
    tmux send-keys -t fwk:3 'reports'
}

function session-daemons
{
    tmux new-session -d -s daemons
    tmux neww -k -n managepy -t daemons:1 
}

function session-hi
{
    tmux new-session -d -s hi
    tmux neww -k -t hi:1
}



for x in $SESSIONS
do
    echo $x
    has-session $x
    except session-$x
done


tmux link-window -dk -s daemons:manage -t hi:0

tmux attach -t hi

















function has-sessions {
    for x in $@ ; do
	echo $x
        tmux has-session -t $x
	rc=$rc+$?
    return rc
}
function try-attach 
{
    echo "In Try"
    tmux has-session -t $1 2>/dev/null
    rc="$?"
    if [ "$rc" -eq "0" ] ; then
        (tmux attach -t $1)
    else
        return $rc
    fi
}
