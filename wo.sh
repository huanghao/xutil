#alias wo="cd ~/workspace"
wo() {
    dir="$HOME/workspace"
    subdir="$dir/$1"
    if [ -d "$subdir" ]; then
        cd $subdir
    else
        cd $dir
    fi
}
_wo() 
{   
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    dir="$HOME/workspace"
    if [ "$cur" == "" ]; then
        opts=$(find $dir -maxdepth 1 -mindepth 1 -type d -exec basename \{} \;)
    else
        opts=$(find $dir -maxdepth 1 -mindepth 1 -type d -name "$cur*" -exec basename \{} \;)
    fi
    
    COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
}
complete -F _wo wo
