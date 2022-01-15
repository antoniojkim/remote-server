#!/usr/bin/env bash

set -e

# Kill any lingering emacs_remote processes
ps -eaf | grep -e "emacs[-_]remote" | grep -v -e 'grep' -e 'tmux' | awk '{print $2}' | xargs kill

declare cmd=${0##*/}
declare -i i
declare -i argc=$#
declare -a argv=("$@")

LEVEL="info"

for ((i=0; i<argc; i++))
do
	case "${argv[i]}" in
	    (-c|c|clean)
            exit 0
            ;;
	    (-d|d|debug)
            LEVEL="debug"
            ;;
    esac
done

pip install .
emacs-remote-client --daemon --host localhost --workspace ~/Documents/Cerebras --level="$LEVEL" &
emacs-remote-client --host localhost --workspace ~/Documents/Cerebras --level="$LEVEL"
wait
