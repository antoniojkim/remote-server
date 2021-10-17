#!/usr/bin/env bash

while
    port=$(shuf -n 1 -i 9130-65535)
    netstat -atun | grep -q "$port"
do
    continue
done

echo "$port"
