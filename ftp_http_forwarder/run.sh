#!/usr/bin/with-contenv bashio

echo running with params \
		-target "$(bashio::config 'target.url')" \
		-user "$(bashio::config 'ftp.user')" \
		-pass "$(bashio::config 'ftp.pass')" \
		-port "$(bashio::config 'ftp.port')" \
		-host "$(bashio::config 'ftp.host')" \
		-passiveports "$(bashio::config 'ftp.passiveports')"
        
/forwarder/go/bin/ftp-http-forwarder \
		-target "$(bashio::config 'target.url')" \
		-user "$(bashio::config 'ftp.user')" \
		-pass "$(bashio::config 'ftp.pass')" \
		-port "$(bashio::config 'ftp.port')" \
		-host "$(bashio::config 'ftp.host')" \
		-passiveports "$(bashio::config 'ftp.passiveports')"
