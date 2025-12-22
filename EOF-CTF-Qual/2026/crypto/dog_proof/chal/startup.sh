#!/bin/sh

ulimit -n 4096

rm /dev/tty
touch /var/log/xinetd.log
chmod 700 /var/log/xinetd.log
ln -s /var/log/xinetd.log /dev/tty

xinetd -dontfork
