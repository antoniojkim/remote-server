#!/usr/bin/env bash
#
cargo build && PATH="$PATH:$(pwd)/target/debug" cargo run --bin emacs-local-client
