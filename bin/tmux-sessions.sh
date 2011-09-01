# Automatically create a new session with these windows

#Register sessions that will be created by this script
SESSIONS="fwk hi daemons"

function try-attach 
{
    tmux has-session -t $1 2>/dev/null
    rc="$?"
    attached="`tmux list-clients -t $1 2>/dev/null`"
    
    if [ "$rc" -eq "0" ] && [ ! "$attached" ]; then
        (tmux attach -t $1)
    else
        return 1
    fi
}

function has-session {
    tmux has-session -t $1 2>/dev/null
}

function list-sessions {
    echo `tmux list-sessions | cut -d: -f1`
    }
function except 
{
    if [ "$?" -eq 1 ] ; then
        $@
    fi
}

function session-fwk 
{
    tmux new-session -d -s fwk
    tmux neww -k -n sreports -t fwk:1
    tmux neww -k -n prod -t fwk:2 
    tmux neww -k  -t fwk:3 
    tmux neww -k -n local -t fwk:4 
    
    tmux send-keys -t fwk:1 'sreports'
    tmux send-keys -t fwk:2 'reports'
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


# Create sessions if they don't exist
for x in $SESSIONS
do
    has-session $x
    except session-$x
done


tmux link-window -dk -s daemons:manage -t hi:0 2>/dev/null

# Attach to session with no attached clients
for x in $(list-sessions) ; do
    try-attach $x && exit 0
    echo "Couldn't attach to session $x"
done















function has-sessions {
    for x in $@ ; do
	echo $x
        tmux has-session -t $x
	rc=$rc+$?
    return rc
    done
}
