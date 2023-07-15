#!/usr/bin/with-contenv bashio

/cloudflare/cloudflared tunnel --no-autoupdate run --token "$(bashio::config 'cloudflare.token')"
