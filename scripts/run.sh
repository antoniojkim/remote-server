#!/usr/bin/env bash
#
cargo build && PATH="$(pwd)/target/debug:$PATH" emacs-local-client --project-dir="/Users/antoniokim/Documents/Projects/emacs-remote"
# cargo build && PATH="$(pwd)/target/debug:$PATH" emacs-remote-client --project-dir="/Users/antoniokim/Documents/Projects/emacs-remote" --client-addr="localhost:9130"
