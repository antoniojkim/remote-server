#!/usr/bin/env bash

if [ -z "$EMACS_REMOTE_PATH" ]; then
    export EMACS_REMOTE_PATH=$HOME/.emacs_remote
fi

mkdir -p $EMACS_REMOTE_PATH
mkdir -p $EMACS_REMOTE_PATH
cd $EMACS_REMOTE_PATH

export PATH=$PATH:$EMACS_REMOTE_PATH/bin
if ! which emacs-remote-server; then
    echo "Could not find emacs-remote-server"
    exit 1
fi

exec emacs-remote-server -r $EMACS_REMOTE_PATH --workspace $WORKSPACE --ports $PORTS --level="$LEVEL"
