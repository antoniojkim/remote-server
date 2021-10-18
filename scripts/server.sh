#!/usr/bin/env bash

function error() {
    printf "ERROR: $*\n"
}
function fail() {
    error "$*"
    exit 1
}

if [ -z "$EMACS_REMOTE_PATH" ]; then
    export EMACS_REMOTE_PATH=$HOME/.emacs_remote
fi

mkdir -p $EMACS_REMOTE_PATH
mkdir -p $EMACS_REMOTE_PATH/scripts
cd $EMACS_REMOTE_PATH

export PATH=$PATH:$EMACS_REMOTE_PATH/bin
if ! which emacs-remote-server; then
    fail "Could not find emacs-remote-server"
fi

emacs-remote-server -r $EMACS_REMOTE_PATH $@
