if [ -e ~/.bash_completion_tmux.sh ]
then
    . ~/.bash_completion_tmux.sh  
fi

export PYTHONPATH=.:$HOME/bookserver/lib
export PATH=~/bbin:~/bin:/Applications/MAMP/Library/bin/:/opt/local/Library/Frameworks/Python.framework/Versions/2.7/bin:/opt/local/bin:/opt/local/sbin:$PATH
export EDITOR=emacs
export CLICOLOR=1
export LSCOLORS=ExFxCxDxBxegedabagacad


alias e="emacs"
alias ipython="ipython-2.7"
alias i=ipython
alias grep="grep --color=auto"
alias ll="ls -ltr"
alias la="ls -al"
alias db="mysql -uroot -proot"

alias screen="screen -xRR -e^Pp"
alias screenn="/usr/bin/screen -e^Pp"
alias fwkscreen="screen -c ~/.screenrc_fwk"

#####
#My repo/alexgaudio.com
#####
alias myg="cd ~/projects/mygit_clone ; pwd"
alias gaudios="ssh gaudios@gaudiosonline.com -D4444 -p22022 -t 'tmux attach || tmux new'" #attach || exec tmux new'"
alias alex="cd ~/mygit_clone/projects/django/alexgaudio/ ; pwd"

alias pygotham="ssh alexg@pythonpeople.net -p4321"


#####
#FWK
#####
alias app1="ssh agaudio@app1.flatworldknowledge.com"
alias app2="ssh agaudio@app2.flatworldknowledge.com -i ~/.ssh/app1/id_rsa"
alias app3="ssh agaudio@app3.flatworldknowledge.com -t 'exec screen -xRR -e ^Oo'"
alias app33="ssh agaudio@app3.flatworldknowledge.com"
alias bert="ssh agaudio@bert.flatworldknowledge.com -t 'exec screen -xRR -e ^Oo'"
alias bertt="ssh agaudio@bert.flatworldknowledge.com"
alias bookdev="ssh agaudio@bookdev.flatworldknowledge.com"
alias buffalo="ssh root@192.168.1.27"
alias gob="ssh agaudio@gob"
alias reports="ssh agaudio@reports.flatworldknowledge.com -t 'exec screen -xRR -e ^Oo'"
alias sreports="ssh ubuntu@stage-reports.flatworldknowledge.com -t -i ~/.ssh/catdev.pem 'exec screen -xRR -e ^Oo'"
alias stage01="ssh agaudio@stage01.flatworldknowledge.com -t 'exec screen -xRR -e ^Oo'"
alias stage011="ssh agaudio@stage01.flatworldknowledge.com"
alias storage01="ssh agaudio@storage01.flatworldknowledge.com"
alias tools="ssh agaudio@tools.flatworldknowledge.com -t 'exec screen -xRR -e ^Oo'"
alias toolss="ssh agaudio@tools.flatworldknowledge.com"
bfwk='agaudio@bert.flatworldknowledge.com:'
sfwk='agaudio@stage01.flatworldknowledge.com:'
afwk='agaudio@app3.flatworldknowledge.com:'
rfwk='agaudio@reports.flatworldknowledge.com:'
srfwk='ubuntu@stage-reports.flatworldknowledge.com:'

#####
#HunchWorks
#####
alias mamp="cd /Applications/MAMP/Library/bin/ ; pwd"
alias hunch="cd ~/projects/HunchWorks ; pwd"
alias hdb='mysql -uroot -proot hunchworks'