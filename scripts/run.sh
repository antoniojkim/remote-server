#!/usr/bin/env bash
#
# cargo build && PATH="$PATH:$(pwd)/target/debug" cargo run --bin emacs-local-client
cargo build && PATH="$(pwd)/target/debug:$PATH" emacs-remote-client --project-dir="/Users/antoniokim/Documents/Projects/emacs-remote" --client-addr="localhost:9130"
