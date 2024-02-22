#!/usr/bin/with-contenv bashio

echo "Hello world!"
id
ls -lah /dev/ttyU* || true

python3 /ptouch/server.py --serial-port="$(bashio::config 'printer_serial_port')" --tcp-port 8099

