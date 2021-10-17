#!/usr/bin/env bash

function error() {
    printf "ERROR: $*\n"
}
function fail() {
    error "$*"
    exit 1
}

declare cmd=${0##*/}
declare -i i
declare -i argc=$#
declare -a argv=("$@")

EMACS_REMOTE_PATH=""
SERVER_ARGS=""

for ((i=0; i<argc; i++))
do
    case "${argv[i]}" in
      (-h|--help|--help=*)
        usage
        exit 0
        ;;
      (-r|--emacs_remote_path)
        EMACS_REMOTE_PATH=${argv[i+1]}
        i++
        ;;
      (*)
        SERVER_ARGS="$SERVER_ARGS ${argv[i]}"
        ;;
    esac
done

if [ -z "$EMACS_REMOTE_PATH" ]; then
    EMACS_REMOTE_PATH=$HOME/.emacs_remote
fi

mkdir -p $EMACS_REMOTE_PATH
mkdir -p $EMACS_REMOTE_PATH/bin
echo "Workspace: $EMACS_REMOTE_PATH"

if [ ! -e $EMACS_REMOTE_PATH/bin/emacs-remote-server ]; then
    fail "emacs-remote-server executable not found"
fi

export PATH=$PATH:$EMACS_REMOTE_PATH/bin
cd $EMACS_REMOTE_PATH

emacs-remote-server -r $EMACS_REMOTE_PATH $SERVER_ARGS
