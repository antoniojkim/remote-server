#!/usr/bin/env bash
#
cargo build

export PATH="$(pwd)/target/debug:$PATH"
emacs-local-client --project-dir="/Users/antoniokim/Documents/Projects/emacs-remote" exit
# cargo build && PATH="$(pwd)/target/debug:$PATH" emacs-remote-client --project-dir="/Users/antoniokim/Documents/Projects/emacs-remote" --client-addr="localhost:9130"
