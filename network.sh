#!/bin/sh
set -v
set -e

if test $# -lt 1; then
    echo "usage: $0 <pid>"
    exit
fi

sudo ip link del veth0 || true

ip link add name veth0 type veth peer name veth1
ip link set veth1 netns $1

ifconfig veth0 10.1.1.2 up
python attach.py $1 ifconfig veth1 10.1.1.1 up
